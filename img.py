from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from PIL import Image
import os
import shutil  # To copy files

def pad(data):
    """Padding for the data to be a multiple of 8 bytes"""
    while len(data) % 8 != 0:
        data += b' '
    return data

def copy_image_to_folder(image_path, folder_path):
    """Copy the image to the folder where the script is located"""
    try:
        # Get the base name of the image file
        image_name = os.path.basename(image_path)
        
        # Define the destination path
        destination_path = os.path.join(folder_path, image_name)

        # Copy the image to the destination folder
        shutil.copy(image_path, destination_path)

        return destination_path
    except Exception as e:
        print(f"An error occurred while copying the image: {e}")
        return None

def encrypt_image(image_path, key, iv):
    try:
        # Open the image and convert it to bytes
        image = Image.open(image_path)
        image_bytes = image.tobytes()

        # Pad the image bytes
        padded_image_bytes = pad(image_bytes)

        # Create the cipher object and encrypt the data
        cipher = DES3.new(key, DES3.MODE_CFB, iv)
        encrypted_bytes = cipher.encrypt(padded_image_bytes)

        # Save the encrypted data to a new file with the same name but .enc extension
        script_dir = os.path.dirname(os.path.abspath(__file__))
        encrypted_image_path = os.path.join(script_dir, os.path.basename(image_path) + '.enc')
        with open(encrypted_image_path, 'wb') as enc_file:
            enc_file.write(encrypted_bytes)

        return encrypted_image_path
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def decrypt_image(encrypted_image_path, key, iv, output_filename):
    try:
        # Read the encrypted image data
        with open(encrypted_image_path, 'rb') as enc_file:
            encrypted_bytes = enc_file.read()

        # Create the cipher object and decrypt the data
        cipher = DES3.new(key, DES3.MODE_CFB, iv)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)

        # Remove padding from decrypted bytes
        decrypted_bytes = decrypted_bytes.rstrip(b' ')

        # Open the original image to extract its mode and size
        original_image = Image.open(encrypted_image_path.replace('.enc', ''))
        decrypted_image = Image.frombytes(original_image.mode, original_image.size, decrypted_bytes)

        # Ensure the output filename has an extension
        if not output_filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            output_filename += '.jpg'  # Default to .jpg if no extension is provided

        # Save the decrypted image in the same folder as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        decrypted_image_path = os.path.join(script_dir, output_filename)
        decrypted_image.save(decrypted_image_path)
    except FileNotFoundError:
        print(f"File not found: {encrypted_image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Generate a random key and IV
key = DES3.adjust_key_parity(get_random_bytes(24))  # DES3 keys are 24 bytes long
iv = get_random_bytes(8)  # DES3 IV is 8 bytes long

# Ask user for the image path
image_path = input("Enter the path to the image file: ").strip()

# Copy the image to the folder where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
copied_image_path = copy_image_to_folder(image_path, script_dir)

if copied_image_path:
    print(f"Image copied and saved to: {copied_image_path}")

    # Encrypt the copied image
    encrypted_image_path = encrypt_image(copied_image_path, key, iv)
    if encrypted_image_path:
        print(f"Encrypted image saved to: {encrypted_image_path}")
        print("Image encrypted successfully!")

        # Ask user if they want to decrypt the image
        decrypt_choice = input("Do you want to decrypt the image? (yes/no): ").strip().lower()
        if decrypt_choice in ('yes', 'y'):
            output_filename = input("Enter the name to save the decrypted image (e.g., decrypted_image.jpg): ").strip()
            decrypt_image(encrypted_image_path, key, iv, output_filename)
            print(f"Decrypted image saved to: {output_filename}")
            print("Image decrypted successfully!")
        else:
            print("Thank you!")
else:
    print("Image copying failed.")
