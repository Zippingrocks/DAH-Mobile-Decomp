/** TEST ACTOR ONLY. Uses the REAL base entity but no AI or movement logic. */
public class j extends o {
    public byte k, f, state;
    public short collisionTimer, stateTimer;
    public c weapon;
    public a secondaryEffect;
    public static int failCall;
    public static boolean changeHealth;
    public void b(int damage) { events.append("damage:"+damage+";"); if(failCall==1)throw new IllegalStateException("scripted damage"); if(changeHealth)e=(short)(e-damage); }
    public void a(int value) { events.append("state:"+value+";"); if(failCall==2)throw new IllegalStateException("scripted state"); state=(byte)value; }
    public short e, shield;
    public boolean c;
    public static byte[] ammo;
    public static StringBuilder events = new StringBuilder();
    public j(int x,int y,int type) { super(x,y,type); events.append("xyz:"+x+","+y+","+type+";"); }
    public j(byte node,int type) { super(0,0,type); k=node; events.append("node:"+node+","+type+";"); }
}
