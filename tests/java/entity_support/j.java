/** TEST ACTOR ONLY. Uses the REAL base entity but no AI or movement logic. */
public class j extends o {
    public byte k;
    public short e, shield;
    public boolean c;
    public static byte[] ammo;
    public static StringBuilder events = new StringBuilder();
    public j(int x,int y,int type) { super(x,y,type); events.append("xyz:"+x+","+y+","+type+";"); }
    public j(byte node,int type) { super(0,0,type); k=node; events.append("node:"+node+","+type+";"); }
}
