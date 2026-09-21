import PIL.Image

#used ascii characters
ASCII_CHARS = [" ", " ", ".", ",", ":", ";", "+", "*", "?", "%", "#", "S", "@"]

#function that resizes the image to the correct format
def resize_image(image, new_width):
    width, height = image.size
    ratio = height / width #find the ratio to allow the height to be adjusted according to the new_width 
    new_height = int(new_width * ratio * 0.5) 
    resized_image = image.resize((new_width, new_height))
    return resized_image

#function that turnes each pixel into grayscale
def grayscale(image):
    grayscale_image = image.convert("L") #L is the intensity of the conversion - L for grayscale :)
    return grayscale_image

#function to convert each "grayscaled_pixel" into the corresponding ascii char
def characterize(image):
    pixels = image.getdata() #returns a list with the grayscale value of each pixel
    characters = "".join([ASCII_CHARS[pixel * len(ASCII_CHARS) // 256] for pixel in pixels]) 
    #return the corresponding ascii char 
    #from the list for each pixel in the created pixel list
    return characters

def main(new_width=160): 
    #attempt to open the image from the user input (path)

    path = input("Enter a valid pathname to the desired image: ")

    try:
        image = PIL.Image.open(path)
    except:
        print(f"""{path} ist not a valid pathname to an image :(
        Gotta do better next time.""")
        exit

    #convert image to ascii
    new_image_data = characterize(grayscale(resize_image(image, new_width)))

    #format
    pixels_count = len(new_image_data)
    ascii_image = "\n".join(new_image_data[i:(i+new_width)] for i in range(0, pixels_count, new_width))

    print(ascii_image)

    with open("ascii_art.txt", "w") as f:
        f.write(ascii_image)

if __name__ == "__main__":
    main()