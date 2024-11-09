/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package guardalloc;

import java.util.ArrayList;
import org.lwjgl.opencl.CLPlatform;

/**
 *
 * @author user
 */
public class Platform {
    String name;
    CLPlatform platform;
    ArrayList<Device> devices=new ArrayList();
    
    Platform(String passed_name, CLPlatform passed_platform){
        name=passed_name;
        platform=passed_platform;
    }
    
}
