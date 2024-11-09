/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package guardalloc;

import com.jme3.app.SimpleApplication;
import com.jme3.input.KeyInput;
import com.jme3.input.MouseInput;
import com.jme3.input.controls.ActionListener;
import com.jme3.input.controls.KeyTrigger;
import com.jme3.input.controls.MouseButtonTrigger;
import com.jme3.material.Material;
import com.jme3.math.ColorRGBA;
import com.jme3.math.Matrix4f;
import com.jme3.math.Vector2f;
import com.jme3.math.Vector3f;
import com.jme3.post.SceneProcessor;
import com.jme3.profile.AppProfiler;
import com.jme3.renderer.Camera;
import com.jme3.renderer.RenderManager;
import com.jme3.renderer.ViewPort;
import com.jme3.renderer.opengl.GL;
import com.jme3.renderer.opengl.GLRenderer;
import com.jme3.renderer.queue.RenderQueue;
import com.jme3.scene.Geometry;
import com.jme3.scene.Mesh;
import com.jme3.scene.VertexBuffer;
import com.jme3.scene.shape.Box;
import com.jme3.texture.FrameBuffer;
import com.jme3.texture.Image;
import com.jme3.util.BufferUtils;
import java.nio.ByteBuffer;
import java.nio.FloatBuffer;
import org.lwjgl.PointerBuffer;
import static org.lwjgl.opencl.CL10.CL_CONTEXT_PLATFORM;
import static org.lwjgl.opencl.CL10.CL_MEM_COPY_HOST_PTR;
import static org.lwjgl.opencl.CL10.CL_MEM_READ_WRITE;
import static org.lwjgl.opencl.CL10.clBuildProgram;
import static org.lwjgl.opencl.CL10.clCreateBuffer;
import static org.lwjgl.opencl.CL10.clCreateCommandQueue;
import static org.lwjgl.opencl.CL10.clCreateContext;
import static org.lwjgl.opencl.CL10.clCreateKernel;
import static org.lwjgl.opencl.CL10.clCreateProgramWithSource;
import static org.lwjgl.opencl.CL10.clEnqueueNDRangeKernel;
import static org.lwjgl.opencl.CL10.clEnqueueReadBuffer;
import static org.lwjgl.opencl.CL10.clFinish;
import static org.lwjgl.opencl.CL10.clReleaseCommandQueue;
import static org.lwjgl.opencl.CL10.clReleaseContext;
import static org.lwjgl.opencl.CL10.clReleaseKernel;
import static org.lwjgl.opencl.CL10.clReleaseMemObject;
import static org.lwjgl.opencl.CL10.clReleaseProgram;
import static org.lwjgl.opencl.CL10.clSetKernelArg;
import org.lwjgl.opencl.CLCommandQueue;
import org.lwjgl.opencl.CLContext;
import org.lwjgl.opencl.CLContextCallback;
import org.lwjgl.opencl.CLDevice;
import org.lwjgl.opencl.CLKernel;
import org.lwjgl.opencl.CLMem;
import org.lwjgl.opencl.CLPlatform;
import org.lwjgl.opencl.CLProgram;

/**
 *
 * @author user
 */
public class OnScreenOGL_Debug extends SimpleApplication implements SceneProcessor {

    String oCLSource = ""
            + "typedef float16 mat4;\n"
            + "float4 mat4VMult(mat4 A, float4 v);\n"
            + "kernel void ScaleKernel(global float *in_vb, global float *matrixI, global float *out_vb, global float *parameters)\n"
            + "{\n"
            + "  float viewPortRight = parameters[0];\n"
            + "  float viewPortLeft = parameters[1];\n"
            + "  float viewPortTop = parameters[2];\n"
            + "  float viewPortBottom = parameters[3];\n"
            + "  float width = parameters[4];\n"
            + "  float height = parameters[5];\n"
            + "  unsigned int idx = get_global_id(0);\n"
            + "  float16 matrix = vload16(0, matrixI);\n"
            + "  float *matrixTest = &matrix;\n"
            + "  float3 pos = vload3(idx, in_vb);\n"
            + "  float *posTest = &pos;\n"
            + "  float4 posR = (float4)( pos, 1.0f );\n"
            + "  float *posRTest = &posR;\n"
            + "  float4 result = mat4VMult(matrix,posR);\n"
            + "  float *resultTest = &result;\n"
            + "  float w = matrixTest[12]*posRTest[0]+matrixTest[13]*posRTest[1]+matrixTest[14]*posRTest[2]+matrixTest[15]*posRTest[3];\n"
            + "  resultTest[0]=resultTest[0]/w;\n"
            + "  resultTest[1]=resultTest[1]/w;\n"
            + "  resultTest[2]=resultTest[2]/w;\n"
            + "  resultTest[0]=((resultTest[0] + 1.0) * (viewPortRight - viewPortLeft) / 2.0 + viewPortLeft) * width;\n"
            + "  resultTest[1]=((resultTest[1] + 1.0) * (viewPortTop - viewPortBottom) / 2.0 + viewPortBottom) * height;\n"
            + "  resultTest[2]=(resultTest[2] + 1.0) / 2.0;\n"
            + "  float3 resultResult = (float3)(resultTest[0],resultTest[1],resultTest[2]);"
            + "  vstore3(resultResult, idx, out_vb);\n"
            //            + "  out_vb[idx]=1.0;\n"
            + "}\n"
            + "\n"
            + "//Computes Av (right multiply of a vector to a matrix)\n"
            + "inline float4 mat4VMult(mat4 A, float4 v) {\n"
            + "    return (float4) (\n"
            + "        dot(A.s0123, v),\n"
            + "        dot(A.s4567, v),\n"
            + "        dot(A.s89ab, v),\n"
            + "        dot(A.scdef, v));\n"
            + "}\n";

    public Terrain terrian;

    FloatBuffer vertices;
    FloatBuffer parameters;
    FloatBuffer matrix;
    FloatBuffer ans;

    CLMem dataToRead1Mem;
    CLMem dataToReadPMem;
    CLMem dataToRead2Mem;
    CLMem answerMem;

    CLContext oCLContext;
    CLCommandQueue queue;
    CLProgram program;
    CLKernel kernel;

    public ViewPort offView;
    FrameBuffer offBuffer;

    private Camera offCamera;

    PointerBuffer kernel1DGlobalWorkSize;

    public Vector3f guardPosition;

    private final ByteBuffer cpuBufD = BufferUtils.createByteBuffer(dBWidth * dBHeight * 4);

    public Vector3f[] positionsOnScreen;
    public float[] verticesRaw;
    public float[] prespectiveParametersRaw;

    Geometry geomSurface;
    Geometry geomPoints;
    Mesh mPoints;

    boolean[] isVertexVisible;

    public float scale = 0.1f;
    public static final int dBWidth = 512, dBHeight = 512;

    public OnScreenOGL_Debug(Terrain passed_terrian, CLPlatform platform, CLDevice device) {
        terrian = passed_terrian;
        prepareVertices();
        initOpenCL(platform, device);
        isVertexVisible = new boolean[terrian.terrainPoints.length * terrian.terrainPoints[0].length * 3];
    }

    @Override
    public void simpleInitApp() {
        cam.setLocation(new Vector3f(0f, 0, 1));
        cam.setFrustumPerspective(80f, 1f, 1f, 50f);
        setupOffscreenView();

        Matrix4f mat4 = offCamera.getViewProjectionMatrix();
        matrix = mat4.toFloatBuffer();
        //Vector3f a = cam.getScreenCoordinates(new Vector3f(0, 0, -1));//TEST!

        prespectiveParametersRaw = new float[6];
        prespectiveParametersRaw[0] = offCamera.getViewPortRight();
        prespectiveParametersRaw[1] = offCamera.getViewPortLeft();
        prespectiveParametersRaw[2] = offCamera.getViewPortTop();
        prespectiveParametersRaw[3] = offCamera.getViewPortBottom();
        prespectiveParametersRaw[4] = offCamera.getWidth();
        prespectiveParametersRaw[5] = offCamera.getHeight();

        feedData(verticesRaw, prespectiveParametersRaw);
        runOcl();
//        destroyCL();

        inputManager.addMapping("focus", new MouseButtonTrigger(MouseInput.BUTTON_LEFT));
        inputManager.addListener(actionListener, "focus");
        inputManager.addMapping("focusAlt", new KeyTrigger(KeyInput.KEY_SPACE));
        inputManager.addListener(actionListener, "focusAlt");
    }

    public void destroyCL() {
        clReleaseKernel(kernel);
        clReleaseProgram(program);
        clReleaseMemObject(dataToRead1Mem);
        clReleaseMemObject(dataToRead2Mem);
        clReleaseMemObject(answerMem);
        clReleaseCommandQueue(queue);
        clReleaseContext(oCLContext);
        //CL.destroy();
    }

    public void setupOffscreenView() {
        offCamera = new Camera(dBWidth, dBHeight);

        // create a pre-view. a view that is rendered before the main view
        offView = renderManager.createPreView("Offscreen View", offCamera);
        offView.setBackgroundColor(ColorRGBA.Black);
        offView.setClearFlags(true, true, true);

        // this will let us know when the scene has been rendered to the 
        // frame buffer
        offView.addProcessor(this);

        // create offscreen framebuffer
        offBuffer = new FrameBuffer(dBWidth, dBHeight, 1);
//        offBuffer.setDepthBuffer(Format.Depth);

        //setup framebuffer's cam
        offCamera.setFrustumPerspective(80f, 1f, 1f, 50f);
        offCamera.setLocation(new Vector3f(0f, 0, 1));
        offCamera.lookAt(new Vector3f(0f, 0f, 0f), Vector3f.UNIT_Y);

        //setup framebuffer's texture
//        offTex = new Texture2D(width, height, Format.RGBA8);
        //setup framebuffer to use renderbuffer
        // this is faster for gpu -> cpu copies
        offBuffer.setDepthBuffer(Image.Format.Depth);
        offBuffer.setColorBuffer(Image.Format.RGBA8);
//        offBuffer.setColorTexture(offTex);

//        depthTexture = new Texture2D(width, height, Image.Format.Depth);
//        offBuffer.setDepthTexture(depthTexture);
        //set viewport to render to offscreen framebuffer
        offView.setOutputFrameBuffer(offBuffer);

//        // setup framebuffer's scene
//        Box boxMesh = new Box(1, 1, 1);
//        Material material = assetManager.loadMaterial("Interface/Logo/Logo.j3m");
//        offBox = new Geometry("box", boxMesh);
//        offBox.setMaterial(material);
//
//        // attach the scene to the viewport to be rendered
//        offView.attachScene(offBox);
        Mesh mSurf = new Mesh();

        int numQuads = (terrian.terrainPoints[0].length - 1) * (terrian.terrainPoints.length - 1);

//        Vector3f[] verticesMat = new Vector3f[terrian.terrainPoints.length * terrian.terrainPoints[0].length];
//        Vector3f[] verticesVisibilityColor = new Vector3f[terrian.terrainPoints.length * terrian.terrainPoints[0].length];
//        Vector2f[] texCoord = new Vector2f[terrian.terrainPoints.length * terrian.terrainPoints[0].length];
//        short[] indexes = new short[numQuads * 2 * 3];
//
//        int vCounter = 0;
//        int counter = 0;
//        for (int i = 0; i < terrian.terrainPoints.length; i++) {
//            for (int j = 0; j < terrian.terrainPoints[0].length; j++) {
//                if (i != terrian.terrainPoints.length - 1 && j != terrian.terrainPoints[0].length - 1) {
//                    indexes[counter] = (short) (i * terrian.terrainPoints[0].length + j);
//                    counter = counter + 1;
//                    indexes[counter] = (short) (i * terrian.terrainPoints[0].length + j + 1);
//                    counter = counter + 1;
//                    indexes[counter] = (short) ((i + 1) * terrian.terrainPoints[0].length + j + 1);
//                    counter = counter + 1;
//
//                    indexes[counter] = (short) (i * terrian.terrainPoints[0].length + j);
//                    counter = counter + 1;
//                    indexes[counter] = (short) ((i + 1) * terrian.terrainPoints[0].length + j + 1);
//                    counter = counter + 1;
//                    indexes[counter] = (short) ((i + 1) * terrian.terrainPoints[0].length + j);
//                    counter = counter + 1;
//
//                }
//                verticesMat[vCounter] = new Vector3f(i * scale, (float) terrian.terrainPoints[i][j] * scale, j * scale);
//                verticesVisibilityColor[vCounter] = new Vector3f(1f, 0f,0f);
//                texCoord[vCounter] = new Vector2f(i % 2, j % 2);
//                vCounter = vCounter + 1;
//            }
//        }
        //\/\/\/\/\/\/TEST
        Vector3f[] verticesMat = new Vector3f[3];
        Vector3f[] verticesVisibilityColor = new Vector3f[3];
        Vector2f[] texCoord = new Vector2f[3];
        short[] indexes = new short[3];
        verticesMat[0] = new Vector3f(0, 0, -1);
        verticesMat[1] = new Vector3f(1, 0, -1);
        verticesMat[2] = new Vector3f(1, 1, -1);
        verticesVisibilityColor[0] = new Vector3f(1, 0, 0);
        verticesVisibilityColor[1] = new Vector3f(1, 0, 0);
        verticesVisibilityColor[2] = new Vector3f(1, 0, 0);
        texCoord[0] = new Vector2f(0, 0);
        texCoord[1] = new Vector2f(1, 0);
        texCoord[2] = new Vector2f(1, 1);
        indexes[0] = 0;
        indexes[1] = 1;
        indexes[2] = 2;
        //^^^^^^^^^^^^TEST

        // Setting buffers
        mSurf.setBuffer(VertexBuffer.Type.Position, 3, BufferUtils.createFloatBuffer(verticesMat));
        mSurf.setBuffer(VertexBuffer.Type.TexCoord, 2, BufferUtils.createFloatBuffer(texCoord));
        mSurf.setBuffer(VertexBuffer.Type.Index, 1, BufferUtils.createShortBuffer(indexes));
        mSurf.setBuffer(VertexBuffer.Type.Color, 3, BufferUtils.createFloatBuffer(verticesVisibilityColor));
        mSurf.updateBound();

        mPoints = mSurf.clone();
        mPoints.setMode(Mesh.Mode.Points);

        // *************************************************************************
        // First mesh uses one solid color
        // *************************************************************************
        // Creating a geometry, and apply a single color material to it
        geomSurface = new Geometry("OurMesh", mSurf);
        Material mat = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
        mat.setColor("Color", ColorRGBA.Blue);
        geomSurface.setMaterial(mat);

//            mPoints.getBuffer(Type.Size)
        geomPoints = new Geometry("OurMeshP", mPoints);
        Material mat1 = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
//        mat1.setColor("Color", ColorRGBA.Red);
        mat1.setBoolean("VertexColor", true);
        geomPoints.setMaterial(mat1);

        // Attaching our geometry to the root node.
        offView.attachScene(geomSurface);
        // Attaching our geometry to the root node.
//        offView.attachScene(geomPoints);

        rootNode.attachChild(geomSurface);
        rootNode.attachChild(geomPoints);

        Box cameraMesh = new Box(0.1f, 0.1f, 0.1f);
        Geometry cameraGeom = new Geometry("box", cameraMesh);
        cameraGeom.setMaterial(mat);
        cameraGeom.setLocalTranslation(offCamera.getLocation());
        rootNode.attachChild(cameraGeom);
//        Material material = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
//        offBox = new Geometry("box", boxMesh);
//        offBox.setMaterial(material);
//
//        // attach the scene to the viewport to be rendered
//        offView.attachScene(offBox);
//        return offTex;
    }

    public Vector3f[] runOcl() {
        clEnqueueNDRangeKernel(queue, kernel, 1, null, kernel1DGlobalWorkSize, null, null, null);
        clEnqueueReadBuffer(queue, answerMem, 1, 0, ans, null, null);
        clFinish(queue);

        positionsOnScreen = new Vector3f[ans.capacity() / 3];
        int counter = 0;
        int internalCounter = 0;
        Vector3f workingVec = null;
        for (int i = 0; i < ans.capacity(); i++) {
            if (internalCounter == 0) {
                workingVec = new Vector3f();
                workingVec.x = ans.get(i);
            } else if (internalCounter == 1) {
                workingVec.y = ans.get(i);
            } else if (internalCounter == 2) {
                workingVec.z = ans.get(i);
            }
//            anst[i] = ans.get(i);
//            if ((i % 3) == 0) {
//                System.out.println(ans.get(i) * cam.getWidth());
//            } else if ((i % 3) + 2 == 0) {
//                System.out.println(ans.get(i) * cam.getHeight());
//            } else {
//            System.out.println(ans.get(i));
//            }
            internalCounter = internalCounter + 1;
            if (internalCounter == 3) {
                positionsOnScreen[counter] = workingVec;
                counter = counter + 1;
                internalCounter = 0;
            }
        }
        return positionsOnScreen;
    }

    private void prepareVertices() {
        if (terrian.terrainPoints.length < 2) {
            System.out.println("MESH MUST HAVE AT LEAST TWO ROWS");
        } else {
//            verticesRaw = new float[terrian.terrainPoints.length * terrian.terrainPoints[0].length * 3];
//            int vCounter = 0;
//            for (int i = 0; i < terrian.terrainPoints.length; i++) {
//                for (int j = 0; j < terrian.terrainPoints[0].length; j++) {
//                    verticesRaw[vCounter] = i * scale;
//                    vCounter = vCounter + 1;
//                    verticesRaw[vCounter] = (float) terrian.terrainPoints[i][j] * scale;
//                    vCounter = vCounter + 1;
//                    verticesRaw[vCounter] = j * scale;
//                    vCounter = vCounter + 1;
//                }
//            }
            //\/\/\/\/\/\/TEST
            verticesRaw = new float[3 * 3];
            verticesRaw[0] = 0;
            verticesRaw[1] = 0;
            verticesRaw[2] = -1;
            verticesRaw[3] = 1;
            verticesRaw[4] = 0;
            verticesRaw[5] = -1;
            verticesRaw[6] = 1;
            verticesRaw[7] = 1;
            verticesRaw[8] = -1;
            //^^^^^^^^^^^^TEST
        }
    }

    private void initOpenCL(CLPlatform platform, CLDevice device) {
        final PointerBuffer ctxProps = org.lwjgl.BufferUtils.createPointerBuffer(3);
        ctxProps.put(CL_CONTEXT_PLATFORM).put(platform.getPointer()).put(0).flip();

        oCLContext = clCreateContext(ctxProps, device, new CLContextCallback() {
            protected void handleMessage(final String errinfo, final ByteBuffer private_info) {
                System.out.println("IN CLContextCallback :: " + errinfo);
            }
        }, null);

        queue = clCreateCommandQueue(oCLContext, device, 0, null);

        program = clCreateProgramWithSource(oCLContext, oCLSource, null);

        clBuildProgram(program, device, "", null);

        kernel = clCreateKernel(program, "ScaleKernel", null);
    }

    @Override
    public void simpleUpdate(float tpf) {
        geomSurface.updateLogicalState(tpf);
        geomSurface.updateGeometricState();

        geomPoints.updateLogicalState(tpf);
        geomPoints.updateGeometricState();

        offCamera.setLocation(new Vector3f(cam.getLocation().x, cam.getLocation().y, cam.getLocation().z));
        offCamera.lookAtDirection(cam.getDirection(), Vector3f.UNIT_Y);
        
        prespectiveParametersRaw = new float[6];
        prespectiveParametersRaw[0] = offCamera.getViewPortRight();
        prespectiveParametersRaw[1] = offCamera.getViewPortLeft();
        prespectiveParametersRaw[2] = offCamera.getViewPortTop();
        prespectiveParametersRaw[3] = offCamera.getViewPortBottom();
        prespectiveParametersRaw[4] = offCamera.getWidth();
        prespectiveParametersRaw[5] = offCamera.getHeight();

        feedData(verticesRaw, prespectiveParametersRaw);
        runOcl();
//        destroyCL();
    }

    @Override
    public void simpleRender(RenderManager rm) {

    }

    @Override
    public void postFrame(FrameBuffer out) {
        updateVisiblePoints();
    }

    public void updateVisiblePoints() {
        cpuBufD.clear();
        readFrameBufferWithGLFormat(offBuffer, cpuBufD, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT);
        Vector3f[] verticesVisibilityColor = new Vector3f[positionsOnScreen.length];

//        for (int i = 0; i < cpuBufD.asFloatBuffer().limit(); i++) {
//            System.out.println("dBZ " + cpuBufD.asFloatBuffer().get(i));
//            System.out.println(i / dBWidth);
//            System.out.println(i % dBHeight);
//            if(cpuBufD.asFloatBuffer().get(i)<1){
//                System.out.println("ABCABC");
//            }
//        }
//        for (int i = 0; i < dBWidth; i++) {
//            for (int j = 0; j < dBHeight; j++) {
//                int ind = (int) (Math.round(i) * dBWidth + Math.round(j));
//                float dBZ = (cpuBufD.getFloat(ind));
//                System.out.print("dBZ " + dBZ);
//            }
//            System.out.println("");
//        }
        float dBZT = (1f - cpuBufD.getFloat(256*512+256));
        System.out.println(dBZT);
        float minDiff=Float.POSITIVE_INFINITY;
        for (int i = 0; i < positionsOnScreen.length; i++) {
            verticesVisibilityColor[i] = new Vector3f(1f, 0f, 0f);
            isVertexVisible[i] = false;
            int[] indices = new int[9];
            indices[0] = (int) (Math.round(positionsOnScreen[i].y) * dBWidth + Math.round(positionsOnScreen[i].x));
            indices[1] = (int) (Math.round(positionsOnScreen[i].y) * dBWidth + Math.round(Math.min(positionsOnScreen[i].x + 1, dBWidth - 1)));
            indices[2] = (int) (Math.round(Math.min(positionsOnScreen[i].y + 1, dBHeight - 1)) * dBWidth + Math.round(Math.min(positionsOnScreen[i].x + 1, dBWidth - 1)));
            indices[3] = (int) (Math.round(Math.min(positionsOnScreen[i].y + 1, dBHeight - 1)) * dBWidth + Math.round(positionsOnScreen[i].x));
            indices[4] = (int) (Math.round(Math.min(positionsOnScreen[i].y + 1, dBHeight - 1)) * dBWidth + Math.round(Math.min(positionsOnScreen[i].x - 1, 0)));
            indices[5] = (int) (Math.round(positionsOnScreen[i].y) * dBWidth + Math.round(Math.min(positionsOnScreen[i].x - 1, 0)));
            indices[6] = (int) (Math.round(Math.min(positionsOnScreen[i].y - 1, 0)) * dBWidth + Math.round(Math.min(positionsOnScreen[i].x - 1, 0)));
            indices[7] = (int) (Math.round(Math.min(positionsOnScreen[i].y - 1, 0)) * dBWidth + Math.round(positionsOnScreen[i].x));
            indices[8] = (int) (Math.round(Math.min(positionsOnScreen[i].y - 1, 0)) * dBWidth + Math.round(Math.min(positionsOnScreen[i].x + 1, dBWidth - 1)));
            for (int m = 0; m < 9; m++) {
                float dBZ = (1f - cpuBufD.getFloat(indices[m]));
                if(Math.abs(dBZ - positionsOnScreen[i].z)<minDiff){
                    minDiff=Math.abs(dBZ - positionsOnScreen[i].z);
                }
//                System.out.println("dBZ " + Math.abs(dBZ - positionsOnScreen[i].z));
                if (Math.abs(dBZ - positionsOnScreen[i].z) < 0.01) {
//                    System.out.println("dBZ " + dBZ);
                    isVertexVisible[i] = true;
                    verticesVisibilityColor[i] = new Vector3f(0f, 1f, 0f);
                }
            }
        }
        System.out.println("minDiff " + minDiff);
//        System.out.println("****");
        VertexBuffer cVB = mPoints.getBuffer(VertexBuffer.Type.Color);
        cVB.updateData(BufferUtils.createFloatBuffer(verticesVisibilityColor));
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

        ((GLRenderer) renderer).gl.glReadPixels(0, 0, dBWidth, dBHeight, glFormat, dataType, byteBuf);
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
    public void cleanup() {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    @Override
    public void setProfiler(AppProfiler profiler) {
//        throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
    }

    public void feedData(float[] at, float[] parameters_in) {
        //float viewPortRight, float viewPortLeft, float viewPortTop, float viewPortBottom, float width, float height
        vertices = org.lwjgl.BufferUtils.createFloatBuffer(at.length).put(at);
        vertices.rewind();
        parameters = org.lwjgl.BufferUtils.createFloatBuffer(parameters_in.length).put(parameters_in);
        parameters.rewind();
//        matrix = org.lwjgl.BufferUtils.createFloatBuffer(bt.length).put(bt);
        matrix.rewind();
        ans = org.lwjgl.BufferUtils.createFloatBuffer(vertices.capacity());

        dataToRead1Mem = clCreateBuffer(oCLContext, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, vertices, null);
        clEnqueueReadBuffer(queue, dataToRead1Mem, 1, 0, vertices, null, null);

        dataToReadPMem = clCreateBuffer(oCLContext, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, parameters, null);
        clEnqueueReadBuffer(queue, dataToReadPMem, 1, 0, parameters, null, null);

        dataToRead2Mem = clCreateBuffer(oCLContext, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, matrix, null);
        clEnqueueReadBuffer(queue, dataToRead2Mem, 1, 0, matrix, null, null);

        answerMem = clCreateBuffer(oCLContext, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, ans, null);

        clFinish(queue);

        clSetKernelArg(kernel, 0, dataToRead1Mem);
        clSetKernelArg(kernel, 1, dataToRead2Mem);
        clSetKernelArg(kernel, 2, answerMem);
        clSetKernelArg(kernel, 3, dataToReadPMem);

        kernel1DGlobalWorkSize = org.lwjgl.BufferUtils.createPointerBuffer(1);
        kernel1DGlobalWorkSize.put(0, at.length / 3);
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

}
