package javax.microedition.lcdui;
import java.awt.GraphicsEnvironment;
import javax.swing.JFrame;
public final class Display {
    private static final Display INSTANCE = new Display();
    private Displayable current;
    private JFrame frame;
    public static Display getDisplay(javax.microedition.midlet.MIDlet midlet) { return INSTANCE; }
    public void setCurrent(Displayable next) {
        current = next;
        if (next instanceof Canvas && !GraphicsEnvironment.isHeadless()) {
            if (frame == null) frame = new JFrame("Destroy All Humans! Mobile");
            ((Canvas)next).mount(frame);
        }
    }
    public Displayable getCurrent() { return current; }
}
