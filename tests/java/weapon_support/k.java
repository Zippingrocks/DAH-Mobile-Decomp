import java.util.Random;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
/** TEST SERVICES ONLY. Draw delegates to the limited headless adapter. */
public final class k extends javax.microedition.lcdui.Displayable {
    public static int failCtor,failStart,failPause,failDestroy;
    public k(GameMidlet owner) {events.append("controller-new;");if(failCtor!=0)throw new IllegalStateException("scripted controller ctor");}
    public void d() {events.append("controller-start;");if(failStart!=0)throw new IllegalStateException("scripted start");}
    public static void e() {events.append("controller-pause;");if(failPause!=0)throw new IllegalStateException("scripted pause");}
    public void f() {events.append("controller-destroy;");if(failDestroy!=0)throw new IllegalStateException("scripted destroy");}

    public static int width, height, c, inputMask;
    public static Random rng;
    public static Graphics graphics;
    public static l font;
    public static g sound;
    public static StringBuilder events = new StringBuilder();
    public static int a(int mask) { events.append("input:"+mask+";"); return mask & inputMask; }
    public static void a(Image image,int x,int y) { graphics.drawImage(image,x,y,20); }
}
