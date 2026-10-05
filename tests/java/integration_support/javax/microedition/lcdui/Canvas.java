package javax.microedition.lcdui;
/** Authored integration contract for the MIDP Canvas API shape used by the game.
 * It supplies deterministic dimensions/input/display hooks only; not a handset renderer.
 */
public abstract class Canvas extends Displayable {
  protected Canvas() {}
  public int getWidth(){return 176;}
  public int getHeight(){return 208;}
  public int getGameAction(int key){return 0;}
  public int getKeyCode(int action){return action;}
  public boolean isShown(){return true;}
  public void repaint(){}
  public void serviceRepaints(){}
  protected void paint(Graphics g){}
  protected void keyPressed(int key){}
  protected void keyReleased(int key){}
  protected void showNotify(){}
  protected void hideNotify(){}
}
