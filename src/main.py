from services.image_overlay.overlay_service import OverlayService
import cv2

def main():
    overlay_service = OverlayService()
    
    # Load images
    user_image = cv2.imread('examples/user_photo.jpg')
    item_image = cv2.imread('examples/clothing_item.png')
    
    # Detect face
    faces = overlay_service.detect_face(user_image)
    
    # Process and display
    # Implementation here

if __name__ == "__main__":
    main()