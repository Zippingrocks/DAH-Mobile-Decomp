package javax.microedition.lcdui;
import java.awt.Dimension;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.image.BufferedImage;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.WindowConstants;
public abstract class Canvas extends Displayable {
    private final BufferedImage framebuffer = new BufferedImage(176, 208, BufferedImage.TYPE_INT_ARGB);
    private final Graphics graphics = new Graphics(framebuffer);
    private volatile boolean shown = true;
    private JPanel panel;
    protected Canvas() {}
    public int getWidth() { return 176; }
    public int getHeight() { return 208; }
    public boolean isShown() { return shown; }
    public int getGameAction(int key) { return 0; }
    public int getKeyCode(int action) { return action; }
    public Graphics desktopGraphics() { return graphics; }
    public void repaint() { paint(graphics); if (panel != null) panel.repaint(); }
    public void serviceRepaints() { if (panel != null) panel.paintImmediately(0,0,panel.getWidth(),panel.getHeight()); }
    void mount(JFrame frame) {
        panel = new JPanel() {
            protected void paintComponent(java.awt.Graphics g) {
                super.paintComponent(g);
                g.drawImage(framebuffer, 0, 0, getWidth(), getHeight(), null);
            }
        };
        panel.setPreferredSize(new Dimension(528, 624));
        panel.setFocusable(true);
        panel.addKeyListener(new KeyAdapter() {
            public void keyPressed(KeyEvent e) { Canvas.this.keyPressed(map(e)); }
            public void keyReleased(KeyEvent e) { Canvas.this.keyReleased(map(e)); }
        });
        frame.setContentPane(panel);
        frame.pack();
        frame.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        frame.setVisible(true);
        panel.requestFocusInWindow();
    }
    private int map(KeyEvent e) {
        switch (e.getKeyCode()) {
            case KeyEvent.VK_LEFT: return 52;
            case KeyEvent.VK_RIGHT: return 54;
            case KeyEvent.VK_UP: return 50;
            case KeyEvent.VK_DOWN: return 56;
            case KeyEvent.VK_ENTER: return 53;
            case KeyEvent.VK_ESCAPE: return -7;
            default:
                char c = e.getKeyChar();
                return Character.isDigit(c) ? c : 0;
        }
    }
    protected void paint(Graphics g) {}
    protected void keyPressed(int key) {}
    protected void keyReleased(int key) {}
    protected void showNotify() { shown = true; }
    protected void hideNotify() { shown = false; }
}
