package javax.microedition.lcdui;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.util.*;
import java.util.List;
/** TEST ADAPTER ONLY. Records calls and rasterizes tested operations
 * into a headless BufferedImage. Both original/rebuilt use the SAME adapter.
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
        long right = Math.min(176L, (long)a + Math.max(0,c));
        long bottom = Math.min(208L, (long)b + Math.max(0,d));
        x = Math.max(0,a); y = Math.max(0,b);
        width = (int)Math.max(0L,right-x); height = (int)Math.max(0L,bottom-y);
    }
    public void drawImage(Image image, int a, int b, int anchor) {
        calls.add("draw:"+(image==null?"null":image.path)+":"+a+","+b+","+anchor);
        if (draws++ == throwAtDraw) throw new IllegalStateException("scripted draw failure");
        if (image == null) throw new NullPointerException("image");
        int dx=a, dy=b;
        int h=anchor & (1|4|8), v=anchor & (2|16|32);
        if (h==1) dx-=image.getWidth()/2; else if(h==8) dx-=image.getWidth(); else if(h!=4) throw new IllegalArgumentException("unsupported horizontal image anchor: "+anchor);
        if (v==2) dy-=image.getHeight()/2; else if(v==32) dy-=image.getHeight(); else if(v!=16) throw new IllegalArgumentException("unsupported vertical image anchor: "+anchor);
        Graphics2D g = canvas.createGraphics();
        try { g.setClip(x,y,width,height); g.drawImage(image.pixels,dx,dy,null); }
        finally { g.dispose(); }
    }
    public void setColor(int rgb) { calls.add("color:"+rgb); color=rgb; }
    public void setColor(int r,int g,int b) {calls.add("color3:"+r+","+g+","+b);color=((r&255)<<16)|((g&255)<<8)|(b&255);}
    public void fillRoundRect(int a,int b,int w,int h,int aw,int ah) {calls.add("fillRound:"+a+","+b+","+w+","+h+","+aw+","+ah);Graphics2D g=canvas.createGraphics();try{g.setClip(x,y,width,height);g.setColor(new Color(color));g.fillRoundRect(a,b,w,h,aw,ah);}finally{g.dispose();}}
    public void drawRoundRect(int a,int b,int w,int h,int aw,int ah) {calls.add("drawRound:"+a+","+b+","+w+","+h+","+aw+","+ah);if(draws++==throwAtDraw)throw new IllegalStateException("scripted round-rect failure");Graphics2D g=canvas.createGraphics();try{g.setClip(x,y,width,height);g.setColor(new Color(color));g.drawRoundRect(a,b,w,h,aw,ah);}finally{g.dispose();}}
    public void fillRect(int a,int b,int w,int h) {calls.add("fill:"+a+","+b+","+w+","+h);Graphics2D g=canvas.createGraphics();try{g.setClip(x,y,width,height);g.setColor(new Color(color));g.fillRect(a,b,w,h);}finally{g.dispose();}}
    private int stroke;
    public void setStrokeStyle(int style) {calls.add("stroke:"+style);if(style!=0&&style!=1)throw new IllegalArgumentException("unsupported test stroke");stroke=style;}
    public void drawLine(int a,int b,int c,int d) {calls.add("line:"+a+","+b+","+c+","+d);if(draws++==throwAtDraw)throw new IllegalStateException("scripted line failure");Graphics2D g=canvas.createGraphics();try{g.setClip(x,y,width,height);g.setColor(new Color(color));if(stroke==1)g.setStroke(new BasicStroke(1,0,0,10,new float[]{1,1},0));g.drawLine(a,b,c,d);}finally{g.dispose();}}
    public void drawRect(int a,int b,int w,int h) {calls.add("rect:"+a+","+b+","+w+","+h);if(draws++==throwAtDraw)throw new IllegalStateException("scripted rect failure");Graphics2D g=canvas.createGraphics();try{g.setClip(x,y,width,height);g.setColor(new Color(color));g.drawRect(a,b,w,h);}finally{g.dispose();}}
    public String snapshot() throws Exception {
        MessageDigest md=MessageDigest.getInstance("SHA-256");ByteBuffer row=ByteBuffer.allocate(176*4);
        for(int j=0;j<208;++j){row.clear();for(int i=0;i<176;++i)row.putInt(canvas.getRGB(i,j));md.update(row.array());}
        StringBuilder hex=new StringBuilder();for(byte b:md.digest())hex.append(String.format("%02x",b&255));
        return stroke+":"+color+":"+x+","+y+","+width+","+height+":"+hex+":"+calls.toString();
    }
}
