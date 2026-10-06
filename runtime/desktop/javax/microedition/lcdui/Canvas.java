package javax.microedition.lcdui;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.image.BufferedImage;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.WindowConstants;

public abstract class Canvas extends Displayable {
    private static final int LOGICAL_WIDTH = 176;
    private static final int LOGICAL_HEIGHT = 208;
    private final BufferedImage framebuffer = new BufferedImage(LOGICAL_WIDTH, LOGICAL_HEIGHT, BufferedImage.TYPE_INT_ARGB);
    private final Graphics graphics = new Graphics(framebuffer);
    private volatile boolean shown = true;
    private JPanel panel;

    protected Canvas() {}

    public int getWidth() { return LOGICAL_WIDTH; }
    public int getHeight() { return LOGICAL_HEIGHT; }
    public boolean isShown() { return shown; }
    public int getGameAction(int key) { return 0; }
    public int getKeyCode(int action) { return action; }
    public Graphics desktopGraphics() { return graphics; }

    public void repaint() {
        paint(graphics);
        if (panel != null) panel.repaint();
    }

    public void serviceRepaints() {
        if (panel != null) panel.paintImmediately(0, 0, panel.getWidth(), panel.getHeight());
    }

    static int desktopScale() {
        String raw = System.getProperty("dah.scale", "3");
        try {
            int value = Integer.parseInt(raw);
            return Math.max(1, Math.min(8, value));
        } catch (NumberFormatException ignored) {
            return 3;
        }
    }

    static int mapDesktopKey(int keyCode, char keyChar) {
        switch (keyCode) {
            case KeyEvent.VK_LEFT:
            case KeyEvent.VK_A:
                return 52;
            case KeyEvent.VK_RIGHT:
            case KeyEvent.VK_D:
                return 54;
            case KeyEvent.VK_UP:
            case KeyEvent.VK_W:
                return 50;
            case KeyEvent.VK_DOWN:
            case KeyEvent.VK_S:
                return 56;
            case KeyEvent.VK_ENTER:
            case KeyEvent.VK_SPACE:
                return 53;
            case KeyEvent.VK_Z:
            case KeyEvent.VK_Q:
                return -6;
            case KeyEvent.VK_X:
            case KeyEvent.VK_ESCAPE:
                return -7;
            default:
                return Character.isDigit(keyChar) ? keyChar : 0;
        }
    }

    void mount(JFrame frame) {
        final int scale = desktopScale();
        panel = new JPanel() {
            protected void paintComponent(java.awt.Graphics awt) {
                super.paintComponent(awt);
                Graphics2D g = (Graphics2D)awt.create();
                try {
                    g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
                    g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_OFF);
                    g.drawImage(framebuffer, 0, 0, LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale, null);
                } finally {
                    g.dispose();
                }
            }
        };
        panel.setPreferredSize(new Dimension(LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale));
        panel.setFocusable(true);
        panel.addKeyListener(new KeyAdapter() {
            public void keyPressed(KeyEvent e) {
                int key = mapDesktopKey(e.getKeyCode(), e.getKeyChar());
                if (key != 0) Canvas.this.keyPressed(key);
            }
            public void keyReleased(KeyEvent e) {
                int key = mapDesktopKey(e.getKeyCode(), e.getKeyChar());
                if (key != 0) Canvas.this.keyReleased(key);
            }
        });

        frame.setContentPane(panel);
        frame.pack();
        frame.setResizable(false);
        frame.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        frame.setLocationByPlatform(true);
        frame.setVisible(true);
        panel.requestFocusInWindow();
    }

    protected void paint(Graphics g) {}
    protected void keyPressed(int key) {}
    protected void keyReleased(int key) {}
    protected void showNotify() { shown = true; }
    protected void hideNotify() { shown = false; }
}
