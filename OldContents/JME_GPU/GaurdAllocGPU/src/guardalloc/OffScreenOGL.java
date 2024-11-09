/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package guardalloc;

import com.jme3.app.SimpleApplication;
import com.jme3.material.Material;
import com.jme3.math.ColorRGBA;
import com.jme3.math.Matrix4f;
import com.jme3.math.Vector2f;
import com.jme3.math.Vector3f;
import com.jme3.post.SceneProcessor;
import com.jme3.profile.AppProfiler;

import com.jme3.renderer.RenderManager;
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
import com.jme3.renderer.Camera;
import com.jme3.renderer.ViewPort;
import com.jme3.renderer.opengl.GL;
import com.jme3.renderer.opengl.GLRenderer;
import com.jme3.renderer.queue.RenderQueue;
import com.jme3.scene.Geometry;
import com.jme3.scene.Mesh;
import com.jme3.scene.VertexBuffer;
import com.jme3.scene.shape.Box;
import com.jme3.texture.FrameBuffer;
import com.jme3.texture.FrameBuffer.RenderBuffer;
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
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;

/**
 *
 * @author user
 */
public class OffScreenOGL extends SimpleApplication implements SceneProcessor {

//    private static final Logger LOG = Logger.getLogger(OffScreenOGL.class.getName());
    public Terrain terrian;
    public float scale = 1f;
    public ViewPort offView;
    private Camera offCamera;
//    Texture offTex;
    FrameBuffer offBuffer;
    public Texture2D depthTexture;
    public final BufferedImage depthImage = new BufferedImage(rTTWidth, rTTHeight,
            BufferedImage.TYPE_INT_BGR);
    Geometry geom;
    Geometry geom1;
    boolean isImageReady = false;
    boolean isImageReadyD = false;

    private Geometry offBox;//TEST

    public static final int rTTWidth = 512, rTTHeight = 512;

    public final BufferedImage image = new BufferedImage(rTTWidth, rTTHeight,
            BufferedImage.TYPE_INT_BGR);

    private final ByteBuffer cpuBuf = BufferUtils.createByteBuffer(rTTWidth * rTTHeight * 4);
    private final ByteBuffer cpuBufD = BufferUtils.createByteBuffer(rTTWidth * rTTHeight * 4);

    public Vector3f[] positionsOnScreen;
    public boolean[] isVertexVisible;

//    String sourceOld = ""
//            + "typedef float16 mat4;\n"
//            + "float4 mat4VMult(mat4 A, float4 v);\n"
//            + "kernel void ScaleKernel(global float *in_vb, global float *matrixI, global float* out_vb)\n"
//            + "{\n"
//            + "  unsigned int idx = get_global_id(0);\n"
//            + "  float16 matrix = vload16(0, matrixI);\n"
//            + "  float *matrixTest = &matrix;\n"
//            + "  float3 pos = vload3(idx, in_vb);\n"
//            + "  float *posTest = &pos;\n"
//            + "  float4 posR = (float4)( pos, 1.0f );\n"
//            + "  float *posRTest = &posR;\n"
//            + "  float4 result = mat4VMult(matrix,posR);\n"
//            + "  float *resultTest = &result;\n"
//            + "  float3 resultResult = (float3)(resultTest[0],resultTest[1],resultTest[2]);"
//            + "  vstore3(resultResult, idx, out_vb);\n"
//            //            + "  out_vb[idx]=1.0;\n"
//            + "}\n"
//            + "\n"
//            + "//Computes Av (right multiply of a vector to a matrix)\n"
//            + "inline float4 mat4VMult(mat4 A, float4 v) {\n"
//            + "    return (float4) (\n"
//            + "        dot(A.s0123, v),\n"
//            + "        dot(A.s4567, v),\n"
//            + "        dot(A.s89ab, v),\n"
//            + "        dot(A.scdef, v));\n"
//            + "}\n";
    String source = ""
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

    FloatBuffer vertices;
    FloatBuffer parameters;
    FloatBuffer matrix;
    FloatBuffer ans;

    CLMem dataToRead1Mem;
    CLMem dataToReadPMem;
    CLMem dataToRead2Mem;
    CLMem answerMem;

    CLContext context;
    CLCommandQueue queue;
    CLProgram program;
    CLKernel kernel;

    PointerBuffer kernel1DGlobalWorkSize;

    public float[] verticesRaw;
    public float[] parametersRaw;

    public OffScreenOGL(Terrain passed_terrian, CLPlatform platform, CLDevice device) {
        terrian = passed_terrian;
        prepareVertices();
        initOpenCL(platform, device);
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

    public void setupOffscreenView() {
//        offCamera = cam.clone();
        offCamera = new Camera(rTTWidth, rTTHeight);

        // create a pre-view. a view that is rendered before the main view
        offView = renderManager.createPreView("Offscreen View", offCamera);
        offView.setBackgroundColor(ColorRGBA.Black);
        offView.setClearFlags(true, true, true);

        // this will let us know when the scene has been rendered to the 
        // frame buffer
        offView.addProcessor(this);

        // create offscreen framebuffer
        offBuffer = new FrameBuffer(rTTWidth, rTTHeight, 1);
//        offBuffer.setDepthBuffer(Format.Depth);

        //setup framebuffer's cam
        offCamera.setFrustumPerspective(80f, 1f, 1f, 50f);
        offCamera.setLocation(new Vector3f(6f, 6f, 10f));
        offCamera.lookAt(new Vector3f(0f, 0f, 0f), Vector3f.UNIT_Y);

        //setup framebuffer's texture
//        offTex = new Texture2D(width, height, Format.RGBA8);
        //setup framebuffer to use renderbuffer
        // this is faster for gpu -> cpu copies
        offBuffer.setDepthBuffer(Format.Depth);
        offBuffer.setColorBuffer(Format.RGBA8);
//        offBuffer.setColorTexture(offTex);

        depthTexture = new Texture2D(rTTWidth, rTTHeight, Format.Depth);

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

//        Vector3f[] vertices = new Vector3f[terrian.terrainPoints.length * terrian.terrainPoints[0].length];
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
//                vertices[vCounter] = new Vector3f(i * scale, (float) terrian.terrainPoints[i][j] * scale, j * scale);
//                texCoord[vCounter] = new Vector2f(i % 2, j % 2);
//                vCounter = vCounter + 1;
//            }
//        }
        //\/\/\/\/\/\/TEST
        Vector3f[] vertices = new Vector3f[3];
        Vector2f[] texCoord = new Vector2f[3];
        short[] indexes = new short[3];
        vertices[0] = new Vector3f(0, 0, -1);
        vertices[1] = new Vector3f(1, 0, -1);
        vertices[2] = new Vector3f(1, 1, -1);
        texCoord[0] = new Vector2f(0, 0);
        texCoord[1] = new Vector2f(1, 0);
        texCoord[2] = new Vector2f(1, 1);
        indexes[0] = 0;
        indexes[1] = 1;
        indexes[2] = 2;
        //^^^^^^^^^^^^TEST

        // Setting buffers
        mSurf.setBuffer(VertexBuffer.Type.Position, 3, BufferUtils.createFloatBuffer(vertices));
        mSurf.setBuffer(VertexBuffer.Type.TexCoord, 2, BufferUtils.createFloatBuffer(texCoord));
        mSurf.setBuffer(VertexBuffer.Type.Index, 1, BufferUtils.createShortBuffer(indexes));
        mSurf.updateBound();

        Mesh mPoints = mSurf.clone();
        mPoints.setMode(Mesh.Mode.Points);

        // *************************************************************************
        // First mesh uses one solid color
        // *************************************************************************
        // Creating a geometry, and apply a single color material to it
        geom = new Geometry("OurMesh", mSurf);
        Material mat = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
        mat.setColor("Color", ColorRGBA.Blue);
        geom.setMaterial(mat);

//            mPoints.getBuffer(Type.Size)
        geom1 = new Geometry("OurMeshP", mPoints);
        Material mat1 = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
        mat1.setColor("Color", ColorRGBA.Red);
        geom1.setMaterial(mat1);

        // Attaching our geometry to the root node.
        offView.attachScene(geom);
        // Attaching our geometry to the root node.
        offView.attachScene(geom1);

//        rootNode.attachChild(geom);
//        rootNode.attachChild(geom1);
        // setup framebuffer's scene
//        Box boxMesh = new Box(1, 1, 1);
//        Material material = new Material(assetManager, "Common/MatDefs/Misc/Unshaded.j3md");
//        offBox = new Geometry("box", boxMesh);
//        offBox.setMaterial(material);
//
//        // attach the scene to the viewport to be rendered
//        offView.attachScene(offBox);
//        return offTex;
    }

    @Override
    public void simpleInitApp() {
//        cam.setFrustumPerspective(80f, 1f, 1f, 50f);
        //\/\/\/\/\/\/TEST
//        cam.setFrustumPerspective(120, 1, 0.1f, 100);
        cam.setLocation(new Vector3f(0f, 0, 1));
        //^^^^^^^^^^^^TEST

        setupOffscreenView();

        Matrix4f mat4 = offCamera.getViewProjectionMatrix();
        matrix = mat4.toFloatBuffer();
        //Vector3f a = cam.getScreenCoordinates(new Vector3f(0, 0, -1));//TEST!

        parametersRaw = new float[6];
        parametersRaw[0] = offCamera.getViewPortRight();
        parametersRaw[1] = offCamera.getViewPortLeft();
        parametersRaw[2] = offCamera.getViewPortTop();
        parametersRaw[3] = offCamera.getViewPortBottom();
        parametersRaw[4] = offCamera.getWidth();
        parametersRaw[5] = offCamera.getHeight();

        feedData(verticesRaw, parametersRaw);
        run();
        destroyCL();

    }

    @Override
    public void simpleUpdate(float tpf) {
        geom.updateLogicalState(tpf);
        geom.updateGeometricState();

        geom1.updateLogicalState(tpf);
        geom1.updateGeometricState();

//        offCamera.setLocation(cam.getLocation());
//        offCamera.lookAtDirection(cam.getDirection(), Vector3f.UNIT_Y);
//        offBox.updateLogicalState(tpf);
//        offBox.updateGeometricState();
    }

    @Override
    public void simpleRender(RenderManager rm) {

    }

    @Override
    public void postFrame(FrameBuffer out) {
        updateDepthImageContents();
        updateImageContents();
    }

    public void updateDepthImageContents() {
        if (isImageReadyD == false) {
            cpuBufD.clear();
//            readFrameBufferWithGLFormat(offBuffer, cpuBufD, GL.GL_FLOAT, GL.GL_FLOAT);
            readFrameBufferWithGLFormat(offBuffer, cpuBufD, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT);

            synchronized (depthImage) {
//                Screenshots.convertScreenShot2(cpuBufD.asIntBuffer(), depthImage);
                int counter = 0;
                for (int i = 0; i < depthImage.getWidth(); i++) {
                    for (int j = 0; j < depthImage.getHeight(); j++) {
                        int grayScaled = (int) ((1f - cpuBufD.getFloat(counter)) * 255);
                        counter = counter + 4;
//                        if(grayScaled>0){
//                            System.out.println("ind: "+counter);
//                        }
                        depthImage.setRGB(j, i, new Color(grayScaled, grayScaled, grayScaled).getRGB());
                    }
                }
                isVertexVisible = new boolean[positionsOnScreen.length];
//                for (int i = 0; i < cpuBufD.asFloatBuffer().limit(); i++) {
//                    System.out.println("dBZ " + cpuBufD.asFloatBuffer().get(i));
//                    System.out.println(i/rTTWidth);
//                    System.out.println(i%rTTHeight);
//                }
//                
//                for (int i = 0; i < rTTWidth; i++) {
//                    for (int j = 0; j < rTTHeight; j++) {
//                        int ind = (int) (Math.round(i) * rTTWidth + Math.round(j));
//                        float dBZ = (cpuBufD.getFloat(ind));
//                        System.out.print("dBZ " + dBZ);
//                    }
//                    System.out.println("");
//                }

                counter = 0;
                for (int i = 0; i < positionsOnScreen.length; i++) {
                    int ind = (int) (Math.round(positionsOnScreen[i].y) * depthImage.getWidth() + Math.round(positionsOnScreen[i].x));
//                    System.out.println("point index: "+ind);
                    float dBZ = (1f - cpuBufD.getFloat(ind));
                    if (Math.abs(dBZ - positionsOnScreen[i].z) < 0.0001) //try
                    {
                        isVertexVisible[i] = true;
                        depthImage.setRGB((int) (positionsOnScreen[i].x), (int) (positionsOnScreen[i].y), new Color(255, 0, 0).getRGB());
                        System.out.println("point index: " + ind);
                        System.out.println("VISIBLE!");
                    }
//                    catch(Exception ex){

//                    }
                }

                isImageReadyD = true;

            }
//            FloatBuffer depthBuff = cpuBufD.asFloatBuffer();
//            float[] floatArray = new float[depthBuff.limit()];
//            depthBuff.get(floatArray);
//            for(int i=0;i<floatArray.length;i++){
//                if(floatArray[i]!=1.0){
//                    System.out.println("!!!!!");
//                }
//            }
//            System.out.println("!!!");
        }
//        cpuBuf.clear();
//        renderer.readFrameBuffer(depthBuffer, cpuBuf);
//        Screenshots.convertScreenShot2(cpuBuf.asIntBuffer(), image);
//        synchronized (image) {
//            Screenshots.convertScreenShot2(cpuBuf.asIntBuffer(), image);
//        }
    }

    public void updateImageContents() {
        if (isImageReady == false) {
            cpuBuf.clear();
            renderer.readFrameBuffer(offBuffer, cpuBuf);

            synchronized (image) {
                Screenshots.convertScreenShot2(cpuBuf.asIntBuffer(), image);
                isImageReady = true;
            }
        }
    }

    private void readFrameBufferWithGLFormat(FrameBuffer fb, ByteBuffer byteBuf, int glFormat, int dataType) {
        if (fb != null) {
            RenderBuffer rb = fb.getDepthBuffer();
            if (rb == null) {
                throw new IllegalArgumentException("Specified framebuffer"
                        + " does not have a colorbuffer");
            }

            renderer.setFrameBuffer(fb);
//            if (gl2 != null) {
//                if (context.boundReadBuf != rb.getSlot()) {
//                    gl2.glReadBuffer(GLFbo.GL_COLOR_ATTACHMENT0_EXT + rb.getSlot());
//                    context.boundReadBuf = rb.getSlot();
//                }
//            }
        }
//        else {
////            renderer.gl.setFrameBuffer(null);
//        }

        ((GLRenderer) renderer).gl.glReadPixels(0, 0, rTTWidth, rTTHeight, glFormat, dataType, byteBuf);
    }

    private void initOpenCL(CLPlatform platform, CLDevice device) {
        final PointerBuffer ctxProps = org.lwjgl.BufferUtils.createPointerBuffer(3);
        ctxProps.put(CL_CONTEXT_PLATFORM).put(platform.getPointer()).put(0).flip();

        context = clCreateContext(ctxProps, device, new CLContextCallback() {
            protected void handleMessage(final String errinfo, final ByteBuffer private_info) {
                System.out.println("IN CLContextCallback :: " + errinfo);
            }
        }, null);

        queue = clCreateCommandQueue(context, device, 0, null);

        program = clCreateProgramWithSource(context, source, null);

        clBuildProgram(program, device, "", null);

        kernel = clCreateKernel(program, "ScaleKernel", null);
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

        dataToRead1Mem = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, vertices, null);
        clEnqueueReadBuffer(queue, dataToRead1Mem, 1, 0, vertices, null, null);

        dataToReadPMem = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, parameters, null);
        clEnqueueReadBuffer(queue, dataToReadPMem, 1, 0, parameters, null, null);

        dataToRead2Mem = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, matrix, null);
        clEnqueueReadBuffer(queue, dataToRead2Mem, 1, 0, matrix, null, null);

        answerMem = clCreateBuffer(context, CL_MEM_READ_WRITE | CL_MEM_COPY_HOST_PTR, ans, null);

        clFinish(queue);

        clSetKernelArg(kernel, 0, dataToRead1Mem);
        clSetKernelArg(kernel, 1, dataToRead2Mem);
        clSetKernelArg(kernel, 2, answerMem);
        clSetKernelArg(kernel, 3, dataToReadPMem);

        kernel1DGlobalWorkSize = org.lwjgl.BufferUtils.createPointerBuffer(1);
        kernel1DGlobalWorkSize.put(0, at.length / 3);
    }

    public Vector3f[] run() {
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

    public void destroyCL() {
        clReleaseKernel(kernel);
        clReleaseProgram(program);
        clReleaseMemObject(dataToRead1Mem);
        clReleaseMemObject(dataToRead2Mem);
        clReleaseMemObject(answerMem);
        clReleaseCommandQueue(queue);
        clReleaseContext(context);
        //CL.destroy();
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

}
