FROM python:3.12-slim AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

# tzdata so a TZ= env var actually resolves. Without it the container silently
# runs on UTC, and every naive datetime.now() in the bot — daily task resets,
# cooldowns, embed timestamps — shifts by an hour or two against the host.
RUN apt-get update \
 && apt-get install -y --no-install-recommends tzdata \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /app

COPY . .

# These four paths are gitignored, so they are not in the build context. They
# are bind-mounted at runtime; creating them here means Docker mounts onto an
# existing file/directory of the right type instead of inventing one, and an
# unmounted deployment fails immediately at startup rather than misbehaving.
RUN mkdir -p src/assets src/data/ai_presets \
 && touch src/config.json src/data/hidden_fish.json

# uid/gid 1000 matches `blackbird` on the host, so the bind-mounted state and
# media directories are writable without chowning anything at runtime.
RUN groupadd --gid 1000 babubot \
 && useradd --uid 1000 --gid 1000 --create-home --shell /usr/sbin/nologin babubot \
 && chown -R babubot:babubot /app
USER babubot

# bot.py resolves src/routines/ and src/commands/ relative to the working
# directory, so this must stay /app.
CMD ["python", "bot.py"]
