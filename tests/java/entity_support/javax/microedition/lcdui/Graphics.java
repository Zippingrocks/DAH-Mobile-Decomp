package javax.microedition.lcdui;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.util.*;
import java.util.List;
/** TEST ADAPTER ONLY. Records calls and rasterizes the limited font operations
 * into a headless BufferedImage. Both original/rebuilt use the SAME adapter.
 * Unsupported anchors fail, rather than pretending to implement all Java ME.
 */
public final class Graphics {
    private final BufferedImage canvas = new BufferedImage(176, 208, BufferedImage.TYPE_INT_ARGB);
    private int x, y, width = 176, height = 208;
    public final List<String> calls = new ArrayList<String>();
    public int throwAtDraw = -1;
    private int draws;
    private int color;
    public int getClipX() { calls.add("getX"); return x; }
    public int getClipY() { calls.add("getY"); return y; }
    public int getClipWidth() { calls.add("getW"); return width; }
    public int getClipHeight() { calls.add("getH"); return height; }
    public void setClip(int a, int b, int c, int d) {
        calls.add("clip:"+a+","+b+","+c+","+d);
        // Intersect against this test surface; no transforms or device differences.
        long right = Math.min(176L, (long)a + Math.max(0,c));
        long bottom = Math.min(208L, (long)b + Math.max(0,d));
        x = Math.max(0,a); y = Math.max(0,b);
        width = (int)Math.max(0L,right-x); height = (int)Math.max(0L,bottom-y);
    }
    public void drawImage(Image image, int a, int b, int anchor) {
        calls.add("draw:"+(image==null?"null":image.path)+":"+a+","+b+","+anchor);
        if (draws++ == throwAtDraw) throw new IllegalStateException("scripted draw failure");
        if (image == null) throw new NullPointerException("image");
        if (anchor != 20) throw new UnsupportedOperationException("Only TOP|LEFT tested");
        Graphics2D g = canvas.createGraphics();
        try { g.setClip(x,y,width,height); g.drawImage(image.pixels,a,b,null); }
        finally { g.dispose(); }
    }
    public void setColor(int rgb) { calls.add("color:"+rgb); color=rgb; }
    public void fillRect(int a,int b,int w,int h) {
        calls.add("fill:"+a+","+b+","+w+","+h);
        Graphics2D g=canvas.createGraphics();
        try { g.setClip(x,y,width,height); g.setColor(new Color(color)); g.fillRect(a,b,w,h); }
        finally { g.dispose(); }
    }
    public String snapshot() throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        ByteBuffer row = ByteBuffer.allocate(176*4);
        for(int j=0;j<208;++j) {
            row.clear(); for(int i=0;i<176;++i) row.putInt(canvas.getRGB(i,j));
            md.update(row.array());
        }
        StringBuilder hex = new StringBuilder();
        for(byte b:md.digest()) hex.append(String.format("%02x",b&255));
        return color+":"+x+","+y+","+width+","+height+":"+hex+":"+calls.toString();
    }
}
