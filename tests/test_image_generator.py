from PIL import Image


# Define the image size (width, height)
image_size = (100, 100)

# Create a new image with a white background
image = Image.new('RGB', image_size, color='white')

# Save the image to a file
image.save(r'C:\\Users\\user\\PycharmProjects\\ProjectREST\\tests\\test_data\\test_image.jpg', 'JPEG')