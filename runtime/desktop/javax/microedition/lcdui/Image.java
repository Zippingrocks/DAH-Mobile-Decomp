package javax.microedition.lcdui;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.io.InputStream;
import javax.imageio.ImageIO;
public final class Image {
    final BufferedImage pixels;
    public final String path;
    private Image(String path, BufferedImage pixels) { this.path = path; this.pixels = pixels; }
    public static Image createImage(String path) throws IOException {
        InputStream in = Image.class.getResourceAsStream(path);
        if (in == null) throw new IOException("Missing resource " + path);
        try {
            BufferedImage image = ImageIO.read(in);
            if (image == null) throw new IOException("Unsupported image " + path);
            return new Image(path, image);
        } finally { in.close(); }
    }
    public int getWidth() { return pixels.getWidth(); }
    public int getHeight() { return pixels.getHeight(); }
}
