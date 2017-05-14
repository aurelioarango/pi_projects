//Aurelio Arango
//CS 697

#include "mbed.h"
#include "rtos.h"
#include "x_cube_mems.h"
#include "Terminal.h"


Mutex mux;//lock
DigitalOut led1(LED1);
static X_CUBE_MEMS *sensorboard = X_CUBE_MEMS::Instance();
Thread thread_one, thread_two, thread_three, thread_four,thread_five;
float temperature =0.0, humidity =0.0, pressure =0.0;


Terminal pc(USBTX, USBRX);//to transmit 

//lock the mutex for pc
void send_data(const char * data, float temp_val, float hum_val, float press_val)
{   
    mux.lock();
    pc.printf("%s: %2.2f %2.2f %4.2f \n",data, temp_val, hum_val, press_val);
    //pc.printf("%s : %f %f %f \r\n",data, temp_val, hum_val, press_val);
    //pc.printf("%s : %f %f %f \r\n",data, temp_val, hum_val, press_val);
    mux.unlock();
}
//change LED on / off
void blink()
{
    led1 = !led1;
}

//funtion for LED
void led_thread() {
    while (true) {
        blink();
        Thread::wait(1000);
    }
}
//get temperature data an print
void get_data()
{
    while (true) {
        sensorboard->hts221.GetTemperature(&temperature);
        sensorboard->hts221.GetHumidity(&humidity);
        sensorboard->lps25h.GetPressure(&pressure);
        send_data("Data" ,temperature,humidity,pressure );
        Thread::wait(1000);
    }
}

int main()
{
    //clear the screen
    pc.cls();
    //thread_five.set_priority(osPriorityHigh);
    //start threads
    while(true)
    {
        thread_one.start(led_thread);
        thread_two.start(get_data);
        sleep();
    }
}
