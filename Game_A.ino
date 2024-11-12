const int xPin = A0;  // 조이스틱 x축 핀
const int yPin = A1;  // 조이스틱 y축 핀
const int buttonPin = 7;  // 버튼 핀

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);  // 버튼 입력 핀 설정 (내부 풀업 저항 사용)
  Serial.begin(9600);  // 시리얼 통신 시작
}

void loop() {
  int xValue = analogRead(xPin);  // x축 값 읽기
  int yValue = analogRead(yPin);  // y축 값 읽기
  int buttonState = digitalRead(buttonPin);  // 버튼 상태 읽기

  // 시리얼로 x, y 값과 버튼 상태 전송
  Serial.print("X:");
  Serial.print(xValue);
  Serial.print(" Y:");
  Serial.print(yValue);
  Serial.print(" Button:");
  Serial.println(buttonState);

  delay(100);  // 0.1초마다 전송 (게임 속도에 맞춰 조정 가능)
}
