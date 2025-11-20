import cv2
import json
import argparse
import fitz
import numpy as np
from pathlib import Path


class CoordinateSelector:
    def __init__(self, file_path, output_file="coordinates_output.json"):
        self.file_path = file_path
        self.output_file = output_file
        self.file_extension = Path(file_path).suffix.lower()
        self.is_pdf = self.file_extension == ".pdf"

        if self.is_pdf:
            self.pdf_doc = fitz.open(file_path)
            self.pdf_page = self.pdf_doc[0]
            pix = self.pdf_page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )
            if pix.n == 4:
                self.image = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
            else:
                self.image = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
        else:
            self.image = cv2.imread(file_path)
            if self.image is None:
                raise ValueError(f"Could not load image: {file_path}")

        self.original_image = self.image.copy()
        self.rectangles = []
        self.current_rect = None
        self.drawing = False
        self.start_point = None

        file_type = "PDF" if self.is_pdf else "Image"
        self.window_name = f"Coordinate Selector ({file_type}) - Draw rectangles, Press 'u' to undo, 'r' to reset, 'q' to quit"

        self.load_coordinates()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.image = self.original_image.copy()

                for i, coord in enumerate(self.rectangles):
                    cv2.rectangle(
                        self.image,
                        (coord["x"], coord["y"]),
                        (coord["x"] + coord["width"], coord["y"] + coord["height"]),
                        (0, 255, 0),
                        2,
                    )
                    cv2.putText(
                        self.image,
                        f"#{i + 1}",
                        (coord["x"], coord["y"] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1,
                    )

                cv2.rectangle(self.image, self.start_point, (x, y), (0, 0, 255), 2)

        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                end_point = (x, y)

                x1 = min(self.start_point[0], end_point[0])
                y1 = min(self.start_point[1], end_point[1])
                x2 = max(self.start_point[0], end_point[0])
                y2 = max(self.start_point[1], end_point[1])

                width = x2 - x1
                height = y2 - y1

                if width > 5 and height > 5:
                    rect_data = {"x": x1, "y": y1, "width": width, "height": height}
                    self.rectangles.append(rect_data)
                    self.save_coordinates()

                self.redraw()

    def redraw(self):
        self.image = self.original_image.copy()

        for i, coord in enumerate(self.rectangles):
            cv2.rectangle(
                self.image,
                (coord["x"], coord["y"]),
                (coord["x"] + coord["width"], coord["y"] + coord["height"]),
                (0, 255, 0),
                2,
            )
            cv2.putText(
                self.image,
                f"#{i + 1}",
                (coord["x"], coord["y"] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

    def load_coordinates(self):
        if Path(self.output_file).exists():
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    self.rectangles = json.load(f)
                self.redraw()
            except Exception as e:
                print(f"❌ Error loading coordinates: {e}")

    def save_coordinates(self):
        if not self.rectangles:
            return False

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(self.rectangles, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False

    def reset(self):
        self.rectangles = []
        self.save_coordinates()
        self.redraw()

    def undo(self):
        if self.rectangles:
            self.rectangles.pop()
            self.save_coordinates()
            self.redraw()

    def generate_masked_output(self):
        if not self.rectangles:
            return False

        try:
            if self.is_pdf:
                output_path = "coordinates_output.pdf"
                output_doc = fitz.open(self.file_path)
                output_page = output_doc[0]

                page_rect = output_page.rect
                img_height, img_width = self.image.shape[:2]
                scale_x = page_rect.width / img_width
                scale_y = page_rect.height / img_height

                for coord in self.rectangles:
                    pdf_x = coord["x"] * scale_x
                    pdf_y = coord["y"] * scale_y
                    pdf_width = coord["width"] * scale_x
                    pdf_height = coord["height"] * scale_y

                    rect = fitz.Rect(
                        pdf_x, pdf_y, pdf_x + pdf_width, pdf_y + pdf_height
                    )
                    output_page.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))

                output_doc.save(output_path)
                output_doc.close()
                print(f"✅ {output_path}")
            else:
                output_path = "coordinates_output.png"
                masked_image = self.original_image.copy()

                for coord in self.rectangles:
                    cv2.rectangle(
                        masked_image,
                        (coord["x"], coord["y"]),
                        (coord["x"] + coord["width"], coord["y"] + coord["height"]),
                        (0, 0, 0),
                        -1,
                    )

                cv2.imwrite(output_path, masked_image)
                print(f"✅ {output_path}")

            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        while True:
            cv2.imshow(self.window_name, self.image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                self.generate_masked_output()
                print(f"✅ {self.output_file}")
                break
            elif key == ord("r"):
                self.reset()
            elif key == ord("u"):
                self.undo()

        cv2.destroyAllWindows()

        if self.is_pdf:
            self.pdf_doc.close()


def main():
    parser = argparse.ArgumentParser(
        description="Interactive coordinate selector for sensitive data masking (supports images and PDFs)"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to the input file (image or PDF)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="coordinates_output.json",
        help="Output JSON file path (default: coordinates_output.json)",
    )

    args = parser.parse_args()

    try:
        selector = CoordinateSelector(args.input, args.output)
        selector.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
