"""
AI-Powered Parking Spot Detector
Uses computer vision and pattern recognition to identify available spots
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from loguru import logger


class SpotDetector:
    """Detects available parking spots using image analysis"""
    
    def __init__(self, config: dict):
        self.config = config
        self.debug_mode = config.get('advanced', {}).get('debug_mode', False)
        
        # Color ranges for available spot indicators (green)
        self.green_lower = np.array([35, 100, 100])  # HSV
        self.green_upper = np.array([85, 255, 255])
        
        # Color for executive spots (might be different - e.g., blue/gold)
        self.executive_lower = np.array([100, 100, 100])  # Blue in HSV
        self.executive_upper = np.array([130, 255, 255])
        
        logger.info("🤖 SpotDetector initialized")
    
    def detect_spots_from_screenshot(self, screenshot_path: Path, spot_type: str = "regular") -> List[Dict]:
        """
        Detect available parking spots from screenshot
        
        Args:
            screenshot_path: Path to screenshot image
            spot_type: Type of spots to detect ('regular', 'executive', 'any')
        
        Returns:
            List of detected spots with coordinates and confidence
        """
        logger.info(f"🔍 Analyzing screenshot for {spot_type} spots...")
        
        try:
            # Load image
            img = cv2.imread(str(screenshot_path))
            if img is None:
                logger.error(f"❌ Failed to load image: {screenshot_path}")
                return []
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Detect spots based on type
            if spot_type == "executive":
                spots = self._detect_by_color(hsv, img, self.executive_lower, self.executive_upper, "executive")
            else:
                spots = self._detect_by_color(hsv, img, self.green_lower, self.green_upper, "regular")
            
            # Also try pattern-based detection
            pattern_spots = self._detect_by_pattern(img, spot_type)
            
            # Merge and deduplicate results
            all_spots = self._merge_detections(spots, pattern_spots)
            
            logger.success(f"✅ Detected {len(all_spots)} available {spot_type} spots")
            
            if self.debug_mode:
                self._save_debug_image(img, all_spots, screenshot_path)
            
            return all_spots
            
        except Exception as e:
            logger.error(f"❌ Spot detection failed: {e}")
            return []
    
    def _detect_by_color(self, hsv: np.ndarray, original: np.ndarray, 
                        lower: np.ndarray, upper: np.ndarray, 
                        spot_type: str) -> List[Dict]:
        """Detect spots by color threshold"""
        # Create mask for the target color
        mask = cv2.inRange(hsv, lower, upper)
        
        # Apply morphological operations to reduce noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        spots = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter by size (adjust these thresholds based on actual UI)
            if 100 < area < 10000:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate center point
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Calculate confidence based on circularity
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
                
                spots.append({
                    'id': f'{spot_type}_{i}',
                    'type': spot_type,
                    'position': (center_x, center_y),
                    'bbox': (x, y, w, h),
                    'area': area,
                    'confidence': circularity,
                    'detection_method': 'color'
                })
        
        logger.debug(f"🎨 Color detection found {len(spots)} {spot_type} spots")
        return spots
    
    def _detect_by_pattern(self, img: np.ndarray, spot_type: str) -> List[Dict]:
        """
        Detect spots by looking for common patterns
        - "P" letter followed by number
        - Parking icon
        - Availability indicators
        """
        spots = []
        
        try:
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Try to find "P" + number patterns (e.g., P-123, P123)
            # This would use OCR - for now, we'll use template matching
            
            # Look for circular/rectangular regions that might be spots
            # Using edge detection (currently not used)
            # edges = cv2.Canny(gray, 50, 150)
            
            # Find circles (potential spot indicators)
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=50,
                param1=50,
                param2=30,
                minRadius=10,
                maxRadius=50
            )
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i, circle in enumerate(circles[0, :]):
                    x, y, r = circle
                    
                    spots.append({
                        'id': f'{spot_type}_pattern_{i}',
                        'type': spot_type,
                        'position': (int(x), int(y)),
                        'bbox': (int(x-r), int(y-r), int(2*r), int(2*r)),
                        'radius': int(r),
                        'confidence': 0.7,
                        'detection_method': 'pattern'
                    })
            
            logger.debug(f"🔎 Pattern detection found {len(spots)} potential spots")
            
        except Exception as e:
            logger.warning(f"⚠️ Pattern detection failed: {e}")
        
        return spots
    
    def _merge_detections(self, spots1: List[Dict], spots2: List[Dict]) -> List[Dict]:
        """Merge and deduplicate spot detections"""
        all_spots = spots1 + spots2
        
        if not all_spots:
            return []
        
        # Sort by confidence
        all_spots.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Remove duplicates (spots too close to each other)
        merged = []
        for spot in all_spots:
            pos = spot['position']
            
            # Check if too close to existing spot
            is_duplicate = False
            for existing in merged:
                existing_pos = existing['position']
                distance = np.sqrt((pos[0] - existing_pos[0])**2 + (pos[1] - existing_pos[1])**2)
                
                if distance < 50:  # Threshold in pixels
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if spot.get('confidence', 0) > existing.get('confidence', 0):
                        merged.remove(existing)
                        merged.append(spot)
                    break
            
            if not is_duplicate:
                merged.append(spot)
        
        return merged
    
    def _save_debug_image(self, img: np.ndarray, spots: List[Dict], original_path: Path):
        """Save annotated debug image"""
        debug_img = img.copy()
        
        for spot in spots:
            x, y = spot['position']
            bbox = spot.get('bbox')
            
            # Draw circle at center
            cv2.circle(debug_img, (x, y), 5, (0, 0, 255), -1)
            
            # Draw bounding box if available
            if bbox:
                bx, by, bw, bh = bbox
                cv2.rectangle(debug_img, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
            
            # Add label
            label = f"{spot['id']} ({spot.get('confidence', 0):.2f})"
            cv2.putText(debug_img, label, (x + 10, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        debug_path = original_path.parent / f"debug_{original_path.name}"
        cv2.imwrite(str(debug_path), debug_img)
        logger.debug(f"💾 Debug image saved: {debug_path}")
    
    def analyze_spot_availability_trend(self, screenshots: List[Path]) -> Dict[str, float]:
        """
        Analyze multiple screenshots to understand spot availability patterns
        Useful for predicting best reservation times
        """
        logger.info("📊 Analyzing spot availability trends...")
        
        spot_counts = {
            'executive': [],
            'regular': []
        }
        
        for screenshot in screenshots:
            executive_spots = self.detect_spots_from_screenshot(screenshot, 'executive')
            regular_spots = self.detect_spots_from_screenshot(screenshot, 'regular')
            
            spot_counts['executive'].append(len(executive_spots))
            spot_counts['regular'].append(len(regular_spots))
        
        trends = {
            'executive_avg': np.mean(spot_counts['executive']) if spot_counts['executive'] else 0,
            'executive_max': max(spot_counts['executive']) if spot_counts['executive'] else 0,
            'regular_avg': np.mean(spot_counts['regular']) if spot_counts['regular'] else 0,
            'regular_max': max(spot_counts['regular']) if spot_counts['regular'] else 0,
        }
        
        logger.info(f"📈 Trends: Executive avg={trends['executive_avg']:.1f}, Regular avg={trends['regular_avg']:.1f}")
        return trends


def test_detector():
    """Test the spot detector"""
    config = {'advanced': {'debug_mode': True}}
    detector = SpotDetector(config)
    
    # Test with a sample screenshot if available
    test_screenshots = list(Path('./screenshots').glob('*.png'))
    
    if test_screenshots:
        spots = detector.detect_spots_from_screenshot(test_screenshots[0])
        print(f"Found {len(spots)} spots")
        for spot in spots:
            print(f"  - {spot['id']}: position={spot['position']}, confidence={spot.get('confidence', 0):.2f}")
    else:
        print("No test screenshots found")


if __name__ == "__main__":
    test_detector()
