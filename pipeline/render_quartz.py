"""Re-render PDF pages with macOS Quartz instead of poppler.

Some 2003-2008 exams were made with Mac Word and embed TrueType Symbol fonts with a MacRoman
encoding; poppler draws those glyphs (minus, angle, intersection, product, ...) as empty boxes,
while Quartz renders them correctly.

Usage: python3 pipeline/render_quartz.py <pdf> <out_prefix> [dpi]   -> <out_prefix>-<n>.png
"""
import sys

import Quartz
from Foundation import NSURL


def render(pdf_path, out_prefix, dpi=150):
    doc = Quartz.CGPDFDocumentCreateWithURL(NSURL.fileURLWithPath_(str(pdf_path)))
    scale = dpi / 72.0
    outputs = []
    for i in range(1, Quartz.CGPDFDocumentGetNumberOfPages(doc) + 1):
        page = Quartz.CGPDFDocumentGetPage(doc, i)
        box = Quartz.CGPDFPageGetBoxRect(page, Quartz.kCGPDFMediaBox)
        w, h = int(box.size.width * scale), int(box.size.height * scale)
        ctx = Quartz.CGBitmapContextCreate(None, w, h, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(),
                                           Quartz.kCGImageAlphaNoneSkipLast)
        Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1)
        Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, w, h))
        Quartz.CGContextScaleCTM(ctx, scale, scale)
        Quartz.CGContextTranslateCTM(ctx, -box.origin.x, -box.origin.y)
        Quartz.CGContextDrawPDFPage(ctx, page)
        image = Quartz.CGBitmapContextCreateImage(ctx)
        out = f"{out_prefix}-{i}.png"
        dest = Quartz.CGImageDestinationCreateWithURL(NSURL.fileURLWithPath_(out), "public.png", 1, None)
        Quartz.CGImageDestinationAddImage(dest, image, None)
        Quartz.CGImageDestinationFinalize(dest)
        outputs.append(out)
    return outputs


if __name__ == "__main__":
    print("\n".join(render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 150)))
