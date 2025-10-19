# Script para criar ícone CorpLang
# Como não temos ImageMagick, vou usar Python para criar um ícone simples

from PIL import Image, ImageDraw, ImageFont
import os

# Criar imagem 128x128
size = (128, 128)
img = Image.new("RGBA", size, (26, 21, 39, 255))  # Background roxo escuro
draw = ImageDraw.Draw(img)

# Círculo de fundo com gradiente simulado
for i in range(60):
    alpha = int(255 * (60 - i) / 60)
    color = (166, 85, 247, alpha)  # Roxo com transparência
    draw.ellipse([(64 - 60 + i, 64 - 60 + i), (64 + 60 - i, 64 + 60 - i)], fill=color)

# Texto "CL" no centro
try:
    # Tentar usar fonte do sistema
    font = ImageFont.truetype("arial.ttf", 48)
except:
    # Fallback para fonte padrão
    font = ImageFont.load_default()

# Desenhar texto "CL" centralizado
text = "CL"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (128 - text_width) // 2
y = (128 - text_height) // 2 - 5

# Sombra do texto
draw.text((x + 2, y + 2), text, fill=(0, 0, 0, 128), font=font)
# Texto principal
draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

# Pontos decorativos
points = [
    (30, 30, (251, 191, 36)),  # Amarelo
    (98, 30, (16, 185, 129)),  # Verde
    (30, 98, (6, 182, 212)),  # Ciano
    (98, 98, (245, 158, 11)),  # Laranja
]

for x, y, color in points:
    draw.ellipse([(x - 4, y - 4), (x + 4, y + 4)], fill=color)

# Salvar o ícone
icon_path = "images/corplang-icon.png"
img.save(icon_path, "PNG")
print(f"Ícone criado em: {icon_path}")
