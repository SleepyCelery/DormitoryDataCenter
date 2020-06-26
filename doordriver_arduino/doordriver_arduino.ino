#include <SoftwareSerial.h>
#include <MsTimer2.h>
#define speedmotor 9 //步进速度
#define angle 128    //步进角度
//以上两个参数一般无需修改
#define coils 0.6     //当前参数下电机旋转圈数
#define restartTime 10 //定时重启时间（单位：分钟）

//定义两相其中LA为A，LB为B，LC为C，LD为D
int LA = 3;
int LB = 4;
int LC = 5;
int LD = 6;
int MotorStep = 0;  //步进索引
int MotorCount = 0; //步进时间计数器
int requests_times = 0;
int interuptCount = 0;       //中断计数器

SoftwareSerial mySerial(8, 9); // RX, TX
String backinfo = "进入监听循环...";

//正转，两个参数代表转速和步进量e
//通过延迟控制转速，数字越小，转速越大,扭矩越小
//每步步进角为5.625',步进量数值越大，每次旋转角度越大
void right(unsigned int Speed, unsigned int road)
{
  //步进节拍：A-B-C-D
  while (road)
  {
    switch (MotorStep)
    {
    case 0: //A相通电
      digitalWrite(LB, LOW);
      digitalWrite(LC, LOW);
      digitalWrite(LD, LOW);
      digitalWrite(LA, HIGH); //A
      MotorStep = 1;
      break;
    case 1: //B相通电
      digitalWrite(LA, LOW);
      digitalWrite(LC, LOW);
      digitalWrite(LD, LOW);
      digitalWrite(LB, HIGH); //B
      MotorStep = 2;
      break;
    case 2: //C相通电
      digitalWrite(LA, LOW);
      digitalWrite(LB, LOW);
      digitalWrite(LD, LOW);
      digitalWrite(LC, HIGH); //C
      MotorStep = 3;
      break;
    case 3: //D相通电
      digitalWrite(LA, LOW);
      digitalWrite(LB, LOW);
      digitalWrite(LC, LOW);
      digitalWrite(LD, HIGH); //D
      MotorStep = 0;
      break;
    }
    delay(Speed); //这里的延时即控制转速
    road--;       //完成一步
  }
  //将四个脚复位0，停止
  for (int i = 3; i < 7; i++)
  {
    digitalWrite(i, LOW);
  }
  MotorCount++;
}

//反转，两个参数代表转速和步进量
void left(unsigned int Speed, unsigned int road)
{
  //步进节拍：D-C-B-A
  while (road)
  {
    switch (MotorStep)
    {
    case 3:
      digitalWrite(LA, LOW);
      digitalWrite(LC, LOW);
      digitalWrite(LD, LOW);
      digitalWrite(LB, HIGH); //B
      MotorStep = 2;
      break;
    case 2:
      digitalWrite(LB, LOW);
      digitalWrite(LC, LOW);
      digitalWrite(LD, LOW);
      digitalWrite(LA, HIGH); //A
      MotorStep = 1;
      break;
    case 1:
      digitalWrite(LA, LOW);
      digitalWrite(LB, LOW);
      digitalWrite(LC, LOW);
      digitalWrite(LD, HIGH); //D
      MotorStep = 0;
      break;
    case 0:
      digitalWrite(LA, LOW);
      digitalWrite(LB, LOW);
      digitalWrite(LD, LOW);
      digitalWrite(LC, HIGH); //C
      MotorStep = 3;
      break;
    }
    delay(Speed); //这里的延时即控制转速
    road--;       //完成一步
  }
  //将四个脚复位0，停止
  for (int i = 3; i < 7; i++)
  {
    digitalWrite(i, LOW);
  }
  MotorCount++;
}

void door_open()
{
  MsTimer2::stop();
  //开锁
  while (MotorCount < coils * 10) //
    right(speedmotor, angle);
  MotorCount = 0;
  //等待3s
  delay(3000);
  //关锁
  while (MotorCount < coils * 10)
    left(speedmotor, angle);
  MotorCount = 0;
  MsTimer2::start();
}

void initial()
{
  requests_times = 0;
  Serial.println("等待模块重启...");
  mySerial.println("AT+RST");
  delay(5000);
  mySerial.println("AT+CWMODE=1");
  Serial.println("正在设置模块为Station模式...");
  delay(3000);
  mySerial.println("AT+CWJAP=\"190919\",\"190919111111\"");
  Serial.println("正在连接WiFi...");
  delay(5000);
  mySerial.println("AT+CIPMUX=1");
  Serial.println("正在启动多连接模式...");
  delay(3000);
  mySerial.println("AT+CIPSERVER=1,8080");

  Serial.println("正在启动TCP服务器,端口:8080...");
  delay(3000);
  for (int o = 3; o > 0; o--)
  {
    digitalWrite(7, HIGH);
    delay(200);
    digitalWrite(7, LOW);
    delay(200);
  }
  while (mySerial.read() >= 0)
  {
  }
  Serial.println(backinfo);
}

//中断服务程序
void onTimer()
{
  interuptCount++;
}

void setup()
{
  //设置中断，每隔30s进入一次中断服务程序 onTimer()
  MsTimer2::set(30000, onTimer);
  MsTimer2::start();

  //2引脚用于控制重启,初始为高
  //将RESET引脚电平置为高,电平为低则重启,注意,此代码具有高的优先级,不可放到其他代码后面!
  digitalWrite(2, HIGH);
  pinMode(2, OUTPUT);
  //初始化其他引脚
  for (int i = 3; i <= 7; i++)
  {
    pinMode(i, OUTPUT);
  }
  Serial.begin(9600);
  mySerial.begin(9600);
  Serial.println("等待模块重启...");
  mySerial.println("AT+RST");
  delay(5000);
  mySerial.println("AT+CWMODE=1");
  Serial.println("正在设置模块为Station模式...");
  delay(3000);
  mySerial.println("AT+CWJAP=\"190919\",\"190919111111\"");
  Serial.println("正在连接WiFi...");
  delay(5000);
  mySerial.println("AT+CIPMUX=1");
  Serial.println("正在启动多连接模式...");
  delay(3000);
  mySerial.println("AT+CIPSERVER=1,8080");

  Serial.println("正在启动TCP服务器,端口:8080...");
  delay(3000);
  for (int o = 3; o > 0; o--)
  {
    digitalWrite(7, HIGH);
    delay(200);
    digitalWrite(7, LOW);
    delay(200);
  }
  while (mySerial.read() >= 0)
  {
  }
  Serial.println(backinfo);
}
void loop()
{
  if (requests_times >= 3)
  {
    initial();
  }
  if (mySerial.available())
  {
    backinfo = mySerial.readString();
    //Serial.println(backinfo);
    //Serial.println(backinfo.length());
    if (backinfo.length() == 35)
    {
      if (backinfo.substring(23, 35) == "190919111111")
      {
        requests_times++;
        mySerial.println("AT+CIPSEND=0,2");
        delay(500);
        mySerial.println("OK");
        delay(500);
        Serial.println("检测到合法指令,运行开门程序!");
        digitalWrite(7, HIGH);
        MsTimer2::stop();//关中断，避免影响步进电机
        door_open();
        digitalWrite(7, LOW);
        while (mySerial.read() >= 0)
        {
        }
      }
      else
      {
        requests_times++;
        Serial.println("检测到非法指令(未找到对应值)!");
        mySerial.println("AT+CIPSEND=0,2");
        delay(500);
        mySerial.println("Er");
        delay(500);
        for (int o = 3; o > 0; o--)
        {
          digitalWrite(7, HIGH);
          delay(200);
          digitalWrite(7, LOW);
          delay(200);
        }
        while (mySerial.read() >= 0)
        {
        }
      }
    }
    else
    {
      requests_times++;
      Serial.println("接收到非法指令(长度检测未通过)!");
      mySerial.println("AT+CIPSEND=0,2");
      delay(500);
      mySerial.println("Er");
      delay(500);
      for (int o = 3; o > 0; o--)
      {
        digitalWrite(7, HIGH);
        delay(200);
        digitalWrite(7, LOW);
        delay(200);
      }
      while (mySerial.read() >= 0)
      {
      }
    }
    MsTimer2::start();
  }
  //设备重启
  if (interuptCount >= restartTime * 2)
  {
    digitalWrite(2, LOW);
    interuptCount = 0;
  }
}
