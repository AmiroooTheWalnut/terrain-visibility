/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package guardalloc;

import org.lwjgl.opencl.CLDevice;

/**
 *
 * @author user
 */
public class Device {
    String name;
    CLDevice device;
    
    Device(String passed_name, CLDevice passed_device){
        name=passed_name;
        device=passed_device;
    }
    
}
