/** TEST WORLD RECORD ONLY. No raycast or area-damage algorithm. No world, score rules, input or actor AI is implemented. */
public final class b {
    public static short b, c, score, worldHeight=800, columns=3, rows=4;
    public static byte scrollStep=1; public static int scrollExtra;
    public static boolean scrollFinished; public static n[] cells;
    public static o interception; public static int failRay, failBlast;
    public static o a(int x1,int y1,int x2,int y2,o owner) {events.append("ray:"+x1+","+y1+","+x2+","+y2+";");if(failRay!=0)throw new IllegalArgumentException("scripted ray");return interception;}
    public static void a(o target,int damage) {events.append("blast:"+damage+";");if(failBlast!=0)throw new IllegalArgumentException("scripted blast");}
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
