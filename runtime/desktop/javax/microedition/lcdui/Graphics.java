package javax.microedition.lcdui;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
public final class Graphics {
    private final BufferedImage canvas;
    private int x, y, width, height, color, stroke;
    public Graphics() { this(new BufferedImage(176, 208, BufferedImage.TYPE_INT_ARGB)); }
    public Graphics(BufferedImage canvas) { this.canvas = canvas; width = canvas.getWidth(); height = canvas.getHeight(); }
    public BufferedImage image() { return canvas; }
    public int getClipX() { return x; }
    public int getClipY() { return y; }
    public int getClipWidth() { return width; }
    public int getClipHeight() { return height; }
    public void setClip(int a, int b, int c, int d) {
        long right = Math.min(canvas.getWidth(), (long)a + Math.max(0, c));
        long bottom = Math.min(canvas.getHeight(), (long)b + Math.max(0, d));
        x = Math.max(0, a); y = Math.max(0, b);
        width = (int)Math.max(0, right - x); height = (int)Math.max(0, bottom - y);
    }
    private Graphics2D graphics() {
        Graphics2D g = canvas.createGraphics();
        g.setClip(x, y, width, height);
        g.setColor(new Color(color));
        if (stroke == 1) g.setStroke(new BasicStroke(1, 0, 0, 10, new float[]{1, 1}, 0));
        return g;
    }
    public void drawImage(Image image, int a, int b, int anchor) {
        if (image == null) throw new NullPointerException("image");
        int dx = a, dy = b;
        int horizontal = anchor & (1 | 4 | 8), vertical = anchor & (2 | 16 | 32);
        if (horizontal == 1) dx -= image.getWidth() / 2; else if (horizontal == 8) dx -= image.getWidth();
        if (vertical == 2) dy -= image.getHeight() / 2; else if (vertical == 32) dy -= image.getHeight();
        Graphics2D g = graphics(); try { g.drawImage(image.pixels, dx, dy, null); } finally { g.dispose(); }
    }
    public void setColor(int rgb) { color = rgb; }
    public void setColor(int r, int g, int b) { color = ((r & 255) << 16) | ((g & 255) << 8) | (b & 255); }
    public void fillRect(int a,int b,int c,int d) { Graphics2D g=graphics(); try{g.fillRect(a,b,c,d);}finally{g.dispose();} }
    public void drawRect(int a,int b,int c,int d) { Graphics2D g=graphics(); try{g.drawRect(a,b,c,d);}finally{g.dispose();} }
    public void drawLine(int a,int b,int c,int d) { Graphics2D g=graphics(); try{g.drawLine(a,b,c,d);}finally{g.dispose();} }
    public void fillRoundRect(int a,int b,int c,int d,int e,int f) { Graphics2D g=graphics(); try{g.fillRoundRect(a,b,c,d,e,f);}finally{g.dispose();} }
    public void drawRoundRect(int a,int b,int c,int d,int e,int f) { Graphics2D g=graphics(); try{g.drawRoundRect(a,b,c,d,e,f);}finally{g.dispose();} }
    public void setStrokeStyle(int style) { stroke = style; }
    public String pixelSha256() throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        ByteBuffer row = ByteBuffer.allocate(canvas.getWidth() * 4);
        for (int yy=0; yy<canvas.getHeight(); yy++) {
            row.clear();
            for (int xx=0; xx<canvas.getWidth(); xx++) row.putInt(canvas.getRGB(xx, yy));
            md.update(row.array());
        }
        StringBuilder out = new StringBuilder();
        for (byte b : md.digest()) out.append(String.format("%02x", b & 255));
        return out.toString();
    }
}
