/** TEST ACTOR ONLY. Uses the REAL base entity but no AI or movement logic. */
public class j extends o {
    public static boolean disguise; public static int disguiseType,globalTimer;
    public int weaponId; public a primaryEffect;
    public static int failCtor,failTick,failDraw,failSwitch,failTransform;
    public void c(int id) {events.append("switch:"+id+";");if(failSwitch!=0)throw new IllegalArgumentException("scripted switch");}
    public void transform(int type,int direction) {events.append("transform:"+type+","+direction+";");if(failTransform!=0)throw new IllegalArgumentException("scripted transform");q=(byte)type;}
    public void l() {events.append("actor-tick;");if(failTick!=0)throw new IllegalArgumentException("scripted actor tick");}
    public void g() {events.append("actor-draw;");if(failDraw!=0)throw new IllegalArgumentException("scripted actor draw");}

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
    public j(int x,int y,int type) { super(x,y,type); if(failCtor!=0)throw new IllegalArgumentException("scripted ctor"); events.append("xyz:"+x+","+y+","+type+";"); }
    public j(byte node,int type) { super(0,0,type); k=node; events.append("node:"+node+","+type+";"); }
}
