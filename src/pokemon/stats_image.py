import discord
import matplotlib.pyplot as plt
from src.utils.file_operations import construct_path, file_exists

IMAGE_PATH = construct_path("tmp/{id}.png")

NAMES = ['HP', 'ATK', 'DEF', 'SP ATK', 'SP DEF', 'SPEED']
# Credits to bulbapedia for the stat hex colors!
COLORS = ['#2EEB5D', '#EED545', '#FD8732', '#48CCD2', '#436BFF', '#C33CFF']
STATS_COUNT = len(NAMES)

class PokemonStatsImage():
    def __init__(self, hp: int, attack: int, defense: int, sp_attack: int, sp_defense: int, speed: int) -> None:
        try:
            self.hp = int(hp)
            self.attack = int(attack)
            self.defense = int(defense)
            self.sp_attack = int(sp_attack)
            self.sp_defense = int(sp_defense)
            self.speed = int(speed)
            self.stats = [self.hp, self.attack, self.defense, self.sp_attack, self.sp_defense, self.speed]
        except Exception as e:
            raise ValueError(f"An error occured while initializing PokemonStats image: {e}")
        self.total = sum(self.stats)
        self.id = "PKMSTATS-" + "-".join([str(stat) for stat in self.stats])
        self.file_name = self.id + ".png"
        self.file_path = IMAGE_PATH.format(id=self.id)

    def _generate(self) -> None:
        plt.figure(figsize=(10, 6), facecolor='#2B2D31')

        for x in range(0, 256, 5):
           plt.axvline(x, color='white', linestyle='-', linewidth=1, alpha=0.1, zorder=1)

        for x in range(20, 256, 20):
           plt.axvline(x, color='grey', linestyle='-', linewidth=1, alpha=0.5, zorder=1)

        # Grey background bars
        plt.barh(range(STATS_COUNT), [255]*STATS_COUNT, color='white', edgecolor='white', alpha=0.05)

        bars = plt.barh(range(STATS_COUNT), self.stats, color=COLORS, edgecolor='white')

        for bar, value in zip(bars, self.stats):
            plt.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f'  {value}',
                    va='center', ha='left', color='white', fontweight='bold', fontsize=20)

        plt.yticks(range(STATS_COUNT), NAMES, fontsize=20, color='white', fontweight='bold')
        plt.xticks([])

        for spine in plt.gca().spines.values():
            spine.set_visible(False)
        plt.gca().set_facecolor('#2B2D31')
        plt.gca().invert_yaxis()

        plt.xlim(0, 255)
        plt.ylim(STATS_COUNT - 0.5, -0.5)

        plt.savefig(self.file_path, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close()

    def exists(self) -> bool:
        return file_exists(self.file_path)

    def get_image_path(self) -> str:
        if not self.exists():
            self._generate()
        return self.file_path
    
    def get_image_file(self) -> discord.File:
        fp = self.get_image_path()
        return discord.File(fp=fp, filename=self.file_name)