/** TEST WORLD RECORD ONLY. No world, score rules, input or actor AI is implemented. */
public final class b {
    public static short b, c, score;
    public static byte mode, p, i, f, d, o;
    public static int s, hitFraction;
    public static short cellWidth=256,cellHeight=256;
    public static byte transferCount;
    public static o[] transfers=new o[256];
    public static j primary, player;
    public static f fallback;
    public static javax.microedition.lcdui.Image hud;
    public static n bucket = new n(0,0);
    public static StringBuilder events = new StringBuilder();
    public static int failSelect;
    public static n a(o entity) {
        events.append("select;");
        if (failSelect == 1) throw new IllegalStateException("scripted select");
        return failSelect == 2 ? null : bucket;
    }
    public static void b(int x,int y) { events.append("clear:"+x+","+y+";"); }
}
