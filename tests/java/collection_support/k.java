import java.util.Random;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
/** TEST SERVICES ONLY. Draw delegates to the limited headless adapter. */
public final class k {
    public static int width, height, c, inputMask;
    public static Random rng;
    public static Graphics graphics;
    public static l font;
    public static g sound;
    public static StringBuilder events = new StringBuilder();
    public static int a(int mask) { events.append("input:"+mask+";"); return mask & inputMask; }
    public static void a(Image image,int x,int y) { graphics.drawImage(image,x,y,20); }
}
