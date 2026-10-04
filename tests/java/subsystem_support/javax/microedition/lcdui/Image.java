package javax.microedition.lcdui;
import java.io.*;
import java.awt.image.BufferedImage;
import java.util.*;
import javax.imageio.ImageIO;
/** TEST ADAPTER ONLY: ImageIO PNG decoding plus scripted failures.
 * No full Java ME image implementation or production platform compatibility claim.
 */
public final class Image {
    public final String path;
    public final BufferedImage pixels;
    public static final List<String> calls = new ArrayList<String>();
    public static int nullsRemaining, failure;
    private Image(String path, BufferedImage pixels) { this.path = path; this.pixels = pixels; }
    public static void reset(int nulls, int mode) { calls.clear(); nullsRemaining = nulls; failure = mode; }
    public static Image createImage(String path) throws IOException {
        calls.add(path);
        if (nullsRemaining > 0) { --nullsRemaining; return null; }
        if (failure == 1) throw new IOException("scripted");
        if (failure == 2) throw new IllegalArgumentException("scripted");
        if (failure == 3) throw new AssertionError("scripted");
        InputStream in = Image.class.getResourceAsStream(path);
        if (in == null) throw new IOException("Missing test image");
        try {
            BufferedImage pixels = ImageIO.read(in);
            if (pixels == null) throw new IOException("Not a PNG test image");
            return new Image(path, pixels);
        } finally { in.close(); }
    }
}
