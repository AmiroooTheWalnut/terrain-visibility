/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package guardalloc;

import com.jme3.app.SimpleApplication;
import com.jme3.asset.AssetKey;
import com.jme3.input.KeyInput;
import com.jme3.input.MouseInput;
import com.jme3.input.controls.ActionListener;
import com.jme3.input.controls.KeyTrigger;
import com.jme3.input.controls.MouseButtonTrigger;
import com.jme3.material.Material;
import com.jme3.material.RenderState;
import com.jme3.math.ColorRGBA;
import com.jme3.renderer.RenderManager;
import com.jme3.scene.Geometry;
import com.jme3.scene.shape.Box;

import com.jme3.scene.Mesh;
import com.jme3.math.Vector2f;
import com.jme3.math.Vector3f;
import com.jme3.post.SceneProcessor;
import com.jme3.profile.AppProfiler;
import com.jme3.renderer.Camera;
import com.jme3.renderer.Renderer;
import com.jme3.renderer.ViewPort;
import com.jme3.renderer.opengl.GL;
import com.jme3.renderer.opengl.GLRenderer;
import com.jme3.renderer.queue.RenderQueue;
import com.jme3.scene.VertexBuffer;
import com.jme3.scene.VertexBuffer.Type;
import com.jme3.system.JmeContext;
import com.jme3.texture.FrameBuffer;
import com.jme3.texture.Image.Format;
import com.jme3.texture.Texture;
import com.jme3.texture.Texture2D;
import com.jme3.util.BufferUtils;
import com.jme3.util.Screenshots;
import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.FloatBuffer;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;

/**
 *
 * @author user
 */
public class Viewing extends SimpleApplication implements SceneProcessor {

    public Terrain terrian;
    public float scale = 0.1f;
    
    Geometry geom;
    Geometry geom1;
    
    public ViewPort offView;
    public Camera offCamera;

    public static final int width = 512, height = 512;
    
    FrameBuffer offBuffer;;

    public final  BufferedImage depthImage = new BufferedImage(width, height, BufferedImage.TYPE_INT_BGR);
    private final ByteBuffer cpuBufD = BufferUtils.createByteBuffer(width * height * 4);
//    private final FloatBuffer cpuBufD = BufferUtils.createFloatBuffer(width * height);

    public Viewing(Terrain passed_terrian) {
        terrian = passed_terrian;
    }

    private ActionListener actionListener = new ActionListener() {
        @Override
        public void onAction(String name, boolean keyPressed, float tpf) {
            if (name.equals("focus") && keyPressed == false) {
                if (inputManager.isCursorVisible() == false) {
                    inputManager.setCursorVisible(true);
                    flyCam.setEnabled(false);
                } else {
                    inputManager.setCursorVisible(false);
                    flyCam.setEnabled(true);
                }
            }
        }
    };

    @Override
    public void simpleInitApp() {
        //\/\/\/\/\/\/TEST
        cam.setFrustumPerspective(120f, 1f, 1f, 50f);
        cam.setLocation(new Vector3f(0f, 0, 1));
        //^^^^^^^^^^^^TEST
        
        
        offCamera = new Camera(width, height);
        offView = renderManager.createPreView("Offscreen View", offCamera);
        offView.setBackgroundColor(ColorRGBA.Black);
        offView.setClearFlags(true, true, true);
        offView.addProcessor(this);
        offBuffer = new FrameBuffer(width, height, 1);
        offCamera.setFrustumPerspective(120f, 1f, 1f, 50f);
        offCamera.setLocation(new Vector3f(cam.getLocation().x, cam.getLocation().y, cam.getLocation().z));
        //offCamera.lookAt(new Vector3f(0f, 0f, 0f), Vector3f.UNIT_Y);
        offBuffer.setDepthBuffer(Format.Depth);
        offBuffer.setColorBuffer(Format.RGBA8);
        offView.setOutputFrameBuffer(offBuffer);
        
        
        inputManager.addMapping("focus", new MouseButtonTrigger(MouseInput.BUTTON_LEFT));
        inputManager.addListener(actionListener, "focus");
        inputManager.addMapping("focusAlt", new KeyTrigger(KeyInput.KEY_SPACE));
        inputManager.addListener(actionListener, "focusAlt");

//        // Vertex positions in space
//        Vector3f[] vertices = new Vector3f[4];
//        vertices[0] = new Vector3f(0, 0, 0);
//        vertices[1] = new Vector3f(3, 0, 0);
//        vertices[2] = new Vector3f(0, 3, 0);
//        vertices[3] = new Vector3f(3, 3, 0);
//
//        // Texture coordinates
//        Vector2f[] texCoord = new Vector2f[4];
//        texCoord[0] = new Vector2f(0, 0);
//        texCoord[1] = new Vector2f(1, 0);
//        texCoord[2] = new Vector2f(0, 1);
//        texCoord[3] = new Vector2f(1, 1);
//
//        // Indexes. We define the order in which mesh should be constructed
//        short[] indexes = {2, 0, 1, 1, 3, 2};
        if (terrian.terrainPoints.length < 2) {
            System.out.println("MESH MUST HAVE AT LEAST TWO ROWS");
        } else {
            Mesh mSurf = new Mesh();

            int numQuads = (terrian.terrainPoints[0].length - 1) * (terrian.terrainPoints.length - 1);

            Vector3f[] vertices = new Vector3f[terrian.terrainPoints.length * terrian.terrainPoints[0].length];
            Vector3f[] verticesSurf = new Vector3f[terrian.terrainPoints.length * terrian.terrainPoints[0].length];
            Vector2f[] texCoord = new Vector2f[terrian.terrainPoints.length * terrian.terrainPoints[0].length];
            short[] indexes = new short[numQuads * 2 * 3];

            int vCounter = 0;
            int counter = 0;
            for (int i = 0; i < terrian.terrainPoints.length; i++) {
                for (int j = 0; j < terrian.terrainPoints[0].length; j++) {
                    if (i != terrian.terrainPoints.length - 1 && j != terrian.terrainPoints[0].length - 1) {
                        indexes[counter] = (short) (i * terrian.terrainPoints[0].length + j);
                        counter = counter + 1;
                        indexes[counter] = (short) (i * terrian.terrainPoints[0].length + j + 1);
                        counter = counter + 1;
                        indexes[counter] = (short) ((i + 1) * terrian.terrainPoints[0].length + j + 1);
                        counter = counter + 1;

                        indexes[counter] = (short) (i * terrian.terrainPoints[0].length + j);
                        counter = counter + 1;
                        indexes[counter] = (short) ((i + 1) * terrian.terrainPoints[0].length + j + 1);
                        counter = counter + 1;
                        indexes[counter] = (short) ((i + 1) * terrian.terrainPoints[0].length + j);
                        counter = counter + 1;

                    }
                    vertices[vCounter] = new Vector3f(i * scale, (float) terrian.terrainPoints[i][j] * scale, j * scale);
                    float offset = 0.01f;
                    float x;
                    float y = (float) (terrian.terrainPoints[i][j] * scale) - offset;
                    float z;
                    if (i == 0) {
                        x = (i * scale) - offset;
                    } else if (i == terrian.terrainPoints.length - 1) {
                        x = (i * scale) + offset;
                    } else {
                        x = (i * scale);
                    }
                    if (j == 0) {
                        z = (j * scale) - offset;
                    } else if (j == terrian.terrainPoints[0].length - 1) {
                        z = (j * scale) + offset;
                    } else {
                        z = (j * scale);
                    }
                    verticesSurf[vCounter] = new Vector3f(x, y, z);
                    texCoord[vCounter] = new Vector2f(i % 2, j % 2);
                    vCounter = vCounter + 1;
                }
            }

            //\/\/\/\/\/\/TEST
//            Vector3f[] vertices = new Vector3f[3];
//            Vector2f[] texCoord = new Vector2f[3];
//            short[] indexes = new short[3];
//            vertices[0]=new Vector3f(0,0,-1);
//            vertices[1]=new Vector3f(1,0,-1);
//            vertices[2]=new Vector3f(1,1,-1);
//            texCoord[0]=new Vector2f(0,0);
//            texCoord[1]=new Vector2f(1,0);
//            texCoord[2]=new Vector2f(1,1);
//            indexes[0]=0;
//            indexes[1]=1;
//            indexes[2]=2;
            //^^^^^^^^^^^^TEST
            // Setting buffers
            mSurf.setBuffer(Type.Position, 3, BufferUtils.createFloatBuffer(verticesSurf));
            mSurf.setBuffer(Type.TexCoord, 2, BufferUtils.createFloatBuffer(texCoord));
            mSurf.setBuffer(Type.Index, 1, BufferUtils.createShortBuffer(indexes));
            mSurf.updateBound();

            Mesh mPoints = new Mesh();
//            Mesh mPoints = mSurf.deepClone();

            mPoints.setBuffer(Type.Position, 3, BufferUtils.createFloatBuffer(vertices));
            mPoints.setBuffer(Type.TexCoord, 2, BufferUtils.createFloatBuffer(texCoord));
            mPoints.setBuffer(Type.Index, 1, BufferUtils.createShortBuffer(indexes));
            mPoints.updateBound();

//            mPoints.setBuffer(Type.Position, 3, BufferUtils.createFloatBuffer(verticesSurf));
            mPoints.setMode(Mesh.Mode.Points);

            // *************************************************************************
            // First mesh uses one solid color
            // *************************************************************************
            // Creating a geometry, and apply a single color material to it
            geom = new Geometry("OurMesh", mSurf);
            Material mat = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
            mat.setColor("Color", ColorRGBA.Blue);
            mat.getAdditionalRenderState().setFaceCullMode(RenderState.FaceCullMode.Off);
            geom.setMaterial(mat);

            // Attaching our geometry to the root node.
            rootNode.attachChild(geom);

//            mPoints.getBuffer(Type.Size)
            geom1 = new Geometry("OurMeshP", mPoints);
            mat = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
            mat.setColor("Color", ColorRGBA.Red);
            geom1.setMaterial(mat);

            // Attaching our geometry to the root node.
            rootNode.attachChild(geom1);
            
            offView.attachScene(geom);

//            b.setShader(shader);
            System.out.println("!!!");
            
            
            
        }

//        Box b = new Box(1, 1, 1); // create cube shape
//        Geometry geom = new Geometry("Box", b);  // create cube geometry from the shape
//        Material mat = new Material(assetManager,
//                "Common/MatDefs/Misc/Unshaded.j3md");  // create a simple material
//        mat.setColor("Color", ColorRGBA.Blue);   // set color of material to blue
//        geom.setMaterial(mat);                   // set the cube's material
//        rootNode.attachChild(geom);              // make the cube appear in the scene
    }

    @Override
    public void simpleUpdate(float tpf) {
//        updateImageContents();
        offCamera.setLocation(new Vector3f(cam.getLocation().x, cam.getLocation().y, cam.getLocation().z));
        offCamera.lookAtDirection(cam.getDirection(), Vector3f.UNIT_Y);
    }

    @Override
    public void simpleRender(RenderManager rm) {
        
//        this.getViewPort().getOutputFrameBuffer().setDepthTexture(depthTexture);
//        for(int i=0;i<rm.getMainViews().size();i++){
//            System.out.println(rm.getMainViews().get(i).getName());
//        }
//        depthBuffer = rm.getMainView("Default").getOutputFrameBuffer().getDepthBuffer();
//        rm.getMainView("Default").getOutputFrameBuffer().setDepthTexture(depthTexture);
//        depthTexture = rm.getMainView("Default").getOutputFrameBuffer().getDepthBuffer().getTexture();
//        System.out.println("!@#!@#");
    }
    

    public void updateImageContents() {
        
    }
    
    public void updateDepthImageContents() {
            cpuBufD.clear();
            
//            readFrameBufferWithGLFormat(offBuffer, cpuBufD, GL.GL_FLOAT, GL.GL_FLOAT);
            readFrameBufferWithGLFormat(offBuffer, cpuBufD, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT);
            
            synchronized (depthImage) {
//                Screenshots.convertScreenShot2(cpuBufD.asIntBuffer(), depthImage);
                int counter=0;
                for (int i = 0; i < depthImage.getWidth(); i++) {
                    for (int j = 0; j < depthImage.getHeight(); j++) {
//                            int col=myApp.depthImage.getRGB(i, j);
//                        float r = new Color(myAppView.depthImage.getRGB(j, i)).getRed();
//                        float g = new Color(myAppView.depthImage.getRGB(j, i)).getGreen();
//                        float b = new Color(myAppView.depthImage.getRGB(j, i)).getBlue();
                        int grayScaled = (int) ((1f-cpuBufD.getFloat(counter)) * 255);
//                        System.out.println(cpuBufD.getFloat(counter));
                        counter=counter+4;
                        
                        depthImage.setRGB(j, i, new Color(grayScaled, grayScaled, grayScaled).getRGB());
                    }
                }
            }
        
    }
    
    private void readFrameBufferWithGLFormat(FrameBuffer fb, ByteBuffer byteBuf, int glFormat, int dataType) {
        if (fb != null) {
            FrameBuffer.RenderBuffer rb = fb.getDepthBuffer();
            if (rb == null) {
                throw new IllegalArgumentException("Specified framebuffer"
                        + " does not have a colorbuffer");
            }
            renderer.setFrameBuffer(fb);
        }

        ((GLRenderer)renderer).gl.glReadPixels(0, 0, 512, 512, glFormat, dataType, byteBuf);
    }

    @Override
    public void initialize(RenderManager rm, ViewPort vp) {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void reshape(ViewPort vp, int w, int h) {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public boolean isInitialized() {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
        return true;
    }

    @Override
    public void preFrame(float tpf) {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void postQueue(RenderQueue rq) {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void postFrame(FrameBuffer out) {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
//        this.getViewPort().getOutputFrameBuffer().setDepthTexture(depthTexture);
        updateDepthImageContents();
    }

    @Override
    public void cleanup() {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void setProfiler(AppProfiler profiler) {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

}
