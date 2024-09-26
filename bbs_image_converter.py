from PIL import Image
import re

# ANSI color escape codes
def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

# Function to convert an image to colored ANSI art (supports transparency handling)
def convert_image_to_colored_ansi(image_path, use_quarter_blocks=False):
    img = Image.open(image_path).convert('RGBA')  # Support images with transparency (RGBA)
    img = img.resize((80, 40))  # Resize image to fit better in the terminal

    shades = " .:-=+*%@#" if not use_quarter_blocks else " ░▒▓█"
    ansi_image = []
    
    for y in range(img.height):
        row = []
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))  # Get RGBA values
            if a == 0:  # Fully transparent pixel
                r, g, b = 255, 255, 255  # Treat transparency as white
            pixel_value = (r + g + b) // 3  # Grayscale value
            color = rgb_to_ansi(r, g, b)
            shade_char = shades[pixel_value // (256 // len(shades))]  # Map grayscale to shade
            row.append(f"{color}{shade_char}\033[0m")  # Add ANSI color and reset
        ansi_image.append("".join(row))
    
    return "\n".join(ansi_image)

# Function to convert an image to colored ASCII art (does not use quarter blocks)
def convert_image_to_colored_ascii(image_path, use_quarter_blocks=False):
    img = Image.open(image_path).convert('RGBA')  # Support images with transparency (RGBA)
    img = img.resize((80, 40))  # Resize image to fit better in the terminal

    # For ASCII mode, quarter blocks are not applicable, so we revert to the standard ASCII character set
    ascii_chars = "@%#*+=-:. "  # Fixed character set for ASCII art
    ascii_image = []
    
    for y in range(img.height):
        row = []
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))  # Get RGBA values
            if a == 0:  # Fully transparent pixel
                r, g, b = 255, 255, 255  # Treat transparency as white
            pixel_value = (r + g + b) // 3  # Grayscale value
            color = rgb_to_ansi(r, g, b)
            char = ascii_chars[pixel_value // (256 // len(ascii_chars))]  # Map grayscale to char
            row.append(f"{color}{char}\033[0m")  # Add ANSI color and reset
        ascii_image.append("".join(row))
    
    return "\n".join(ascii_image)

# BBCode parser with added functionality for /pic command
def bbcode_parser_with_pic(content):
    # Function to handle image conversion if /pic is found
    def insert_image(content, image_path, mode="ansi", colored=True, use_quarter_blocks=False):
        # Remove extra quotes around the image path
        image_path = image_path.strip('"')
        
        if mode == "ansi":
            return convert_image_to_colored_ansi(image_path, use_quarter_blocks=use_quarter_blocks) if colored else convert_image_to_ansi(image_path)
        elif mode == "ascii":
            # In ASCII mode, we ignore the quarter_block option
            return convert_image_to_colored_ascii(image_path, use_quarter_blocks=False) if colored else convert_image_to_ascii(image_path)
        return ""

    # Look for /pic in the content
    match = re.search(r'/pic (\S+)', content)
    if match:
        image_path = match.group(1)  # The second part of the match is the file path
        image_format = input("Choose image format (ansi/ascii): ").lower()
        color_option = input("Would you like to use color? (yes/no): ").lower() == 'yes'
        quarter_block_option = input("Would you like to use quarter blocks for more detail? (yes/no): ").lower() == 'yes'
        
        if image_format == "ascii":
            return content + "\n" + insert_image(content, image_path, mode="ascii", colored=color_option, use_quarter_blocks=quarter_block_option)
        else:
            return content + "\n" + insert_image(content, image_path, mode="ansi", colored=color_option, use_quarter_blocks=quarter_block_option)
    
    return content
