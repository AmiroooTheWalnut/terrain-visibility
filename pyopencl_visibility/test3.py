import numpy as np
import pyopencl as cl
import matplotlib.pyplot as plt

widthT = 20000
heightT = 20000

# rng = np.random.default_rng()
# terrain=rng.random((widthT,heightT), dtype=np.float32)

# Define grid
x = np.linspace(0, widthT - 1, widthT)
y = np.linspace(0, heightT - 1, heightT)
X, Y = np.meshgrid(x, y)

# Mean and covariance
mean = np.array([49, 49])
cov = np.array([[140, 0], [0, 140]])

# Stack coordinates
pos = np.dstack((X, Y))

# Compute multivariate normal manually
diff = pos - mean
inv_cov = np.linalg.inv(cov)
norm_const = 1 / (2 * np.pi * np.sqrt(np.linalg.det(cov)))
exponent = -0.5 * np.einsum('...k,kl,...l->...', diff, inv_cov, diff)

terrain = norm_const * np.exp(exponent) * 10000
terrain = terrain.astype(np.float32)

zBuff = np.zeros((widthT, heightT), dtype=np.float32)
visRes = np.zeros((widthT, heightT), dtype=np.byte)

# a_np = rng.random(50000, dtype=np.float32)
# b_np = rng.random(50000, dtype=np.float32)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
# a_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
# b_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)

terrain_b = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=terrain)
#zBuff_b = cl.Buffer(ctx, mf.WRITE_ONLY | mf.COPY_HOST_PTR, hostbuf=zBuff)
visRes_b = cl.Buffer(ctx, mf.WRITE_ONLY | mf.COPY_HOST_PTR, hostbuf=visRes)

gX = 30
gY = 24
gZ = terrain[gX, gY] + 8
range = 200

prg = cl.Program(ctx, """
__kernel void sum(
    int width, int height, int gX, int gY, float gZ, __global float *tMat, __global char *visRes, float range)
{
    int xT = get_global_id(0);
    int yT = get_global_id(1);
    int idx = yT * width + xT;
    float zT = tMat[idx];
    float disp2D = sqrt(pow(gX-xT,2.0f)+pow(gY-yT,2.0f));
    float distP = sqrt(pow(gX-xT,2.0f)+pow(gY-yT,2.0f)+pow(zT-gZ,2.0f));
    //zBuff[idx]=distP;
    if(disp2D>range){
        return;
    }

    bool isBlocked=0;
    if(xT>-1 && yT>-1){
    //float tempX=round(gX+(0.99f)*(xT-gX));
    //float tempY=round(gY+(0.99f)*(yT-gY));
    //int idxF = tempY * width + tempX;
    //visRes[idxF]=1;
    //tempX=round(gX+(0.8f)*(xT-gX));
    //tempY=round(gY+(0.8f)*(yT-gY));
    //idxF = tempY * width + tempX;
    //visRes[idxF]=1;
    //tempX=round(gX+(0.6f)*(xT-gX));
    //tempY=round(gY+(0.6f)*(yT-gY));
    //idxF = tempY * width + tempX;
    //visRes[idxF]=1;
    //tempX=round(gX+(0.4f)*(xT-gX));
    //tempY=round(gY+(0.4f)*(yT-gY));
    //idxF = tempY * width + tempX;
    //visRes[idxF]=1;
    //tempX=round(gX+(0.2f)*(xT-gX));
    //tempY=round(gY+(0.2f)*(yT-gY));
    //idxF = tempY * width + tempX;
    //visRes[idxF]=1;
    //tempX=round(gX+(0.01f)*(xT-gX));
    //tempY=round(gY+(0.01f)*(yT-gY));
    //idxF = tempY * width + tempX;
    //visRes[idxF]=1;
    for(float i=0;i<=1;i=i+0.01f){
        float vX=round(gX+(i)*(xT-gX));
        float vY=round(gY+(i)*(yT-gY));
        float maxVZ=gZ+(i)*(zT-gZ);
        int vIdx=(vY * width + vX);
        float vZ=tMat[vIdx];
        //zBuff[vIdx]=zT;
        //visRes[vIdx]=1;
        //visRes[idxF]=1;
        if(vZ>maxVZ){
            isBlocked=1;
            break;
        }
    }
    if(isBlocked==0){
        visRes[idx]=1;
    }
    }

}
""").build()

# res_g = cl.Buffer(ctx, mf.WRITE_ONLY, a_np.nbytes)
knl = prg.sum  # Use this Kernel object for repeated calls
global_size = (widthT, heightT)
knl(queue, global_size, None, np.int32(widthT), np.int32(heightT), np.int32(gX), np.int32(gY), np.float32(gZ),
    terrain_b, visRes_b, np.float32(range))

# res_np = np.empty_like(a_np)
# cl.enqueue_copy(queue, res_np, res_g)

#zBuff_res = np.empty_like(zBuff)
#cl.enqueue_copy(queue, zBuff_res, zBuff_b)

visRes_res = np.empty_like(visRes)
cl.enqueue_copy(queue, visRes_res, visRes_b)

# fig = plt.figure(figsize=(8, 6))
# ax = fig.add_subplot(projection='3d')
# X = np.arange(0, widthT, 1)
# Y = np.arange(0, heightT, 1)
# X, Y = np.meshgrid(X, Y)
#
# colors = np.empty(visRes_res.shape + (4,), dtype=np.float32)  # RGBA
# colors[visRes_res == 0] = [0, 0, 1, 1]  # Blue
# colors[visRes_res == 1] = [1, 0, 0, 1]  # Red
#
# ax.plot_surface(X, Y, terrain, facecolors=colors, rstride=1, cstride=1, linewidth=0, antialiased=False)
# plt.show()

# Check on CPU with Numpy:
# error_np = res_np - (a_np + b_np)
# print(f"Error:\n{error_np}")
# print(f"Norm: {np.linalg.norm(error_np):.16e}")
# assert np.allclose(res_np, a_np + b_np)