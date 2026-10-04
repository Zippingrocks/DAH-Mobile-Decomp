package javax.microedition.lcdui;
/** Scripted lifecycle recorder only; not a phone or Windows display. */
public class Display {
    public static StringBuilder events=new StringBuilder();
    public static int failGet,failSet; public static boolean nullGet;
    public static Display instance=new Display(); public Displayable current;
    public static Display getDisplay(javax.microedition.midlet.MIDlet owner) {
        events.append("get-display;"); if(failGet!=0)throw new IllegalArgumentException("scripted display"); return nullGet?null:instance;
    }
    public void setCurrent(Displayable next) {
        events.append("set-current:"+(next==null?"null":"controller")+";");
        if(failSet!=0)throw new IllegalArgumentException("scripted current");current=next;
    }
}
