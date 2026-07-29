# Attention Mission

Transformer 논문 **"Attention Is All You Need"**의 핵심 아이디어를 직접 구현하고 실험하며 이해하기 위한 미션이다.

---

# Mission 1. Self-Attention 직접 구현

## 목표

PyTorch의 `nn.MultiheadAttention`을 사용하지 않고 Self-Attention을 직접 구현한 뒤,
PyTorch 구현과 동일한 결과가 나오는지 확인한다.

## 구현 과정

1. 문장을 토큰으로 분리
2. 입력 임베딩 생성
3. Query(Q), Key(K), Value(V) 생성
4. Attention Score 계산

$$
\frac{QK^T}{\sqrt{d_k}}
$$

5. Softmax 적용
6. Value와 곱하여 최종 출력 생성
7. PyTorch 구현과 결과 비교

## 실험 결과

```
일치 : True
최대 오차 : 2.24e-08
```

직접 구현한 Self-Attention과 PyTorch의 `nn.MultiheadAttention`이 거의 동일한 결과를 출력하였다.

## 배운 점

- Q(Query)는 현재 토큰이 찾고 싶은 정보
- K(Key)는 각 토큰이 가진 특징
- V(Value)는 실제 전달할 정보

Attention은 Q와 K의 유사도를 계산한 뒤, 중요한 V를 가져오는 과정임을 확인하였다.

---

# Mission 2. 왜 √dₖ로 나누는가?

## 목표

Transformer 논문에서 사용하는

$$
\frac{QK^T}{\sqrt{d_k}}
$$

가 필요한 이유를 직접 실험한다.

---

## 실험 1

논문 주장

```python
Var(q·k) = d_k
```

를 실제로 측정하였다.

### 결과

| dₖ | 실측 분산 |
|----|---------|
|2|≈2|
|4|≈4|
|8|≈8|
|16|≈16|
|32|≈32|
|64|≈64|
|128|≈128|
|256|≈256|
|512|≈512|

실험 결과는 논문의 주장과 거의 동일하였다.

---

## 실험 2

Softmax에

```python
QKᵀ
```

를 그대로 넣었을 때와

```python
QKᵀ / √dₖ
```

를 넣었을 때를 비교하였다.

### 결과

- 나누지 않으면
  - 점수가 계속 커진다.
  - Softmax가 포화된다.
  - 한 토큰에만 거의 모든 확률이 집중된다.

- √dₖ로 나누면
  - 점수 크기가 안정된다.
  - Softmax가 적절한 확률을 유지한다.
  - 여러 토큰을 함께 참고할 수 있다.

## 배운 점

차원이 커질수록 QKᵀ의 분산이 커지므로,
Transformer는 √dₖ로 나누어 Softmax의 포화를 방지한다.

---

# Mission 3. Dot Product vs Additive Attention

## 목표

Transformer가 왜 Dot Product Attention을 사용하는지 직접 비교한다.

비교 대상

- Dot Product Attention
- Additive Attention(Bahdanau)

---

## 1. 실행 속도 비교

| 문장 길이 | Dot Product | Additive | 느린 정도 |
|-----------|------------|----------|----------|
|64|0.029ms|0.264ms|9배|
|128|0.058ms|0.812ms|14배|
|256|0.101ms|4.912ms|49배|
|512|0.133ms|19.044ms|143배|

문장이 길어질수록 Additive Attention이 훨씬 느려지는 것을 확인하였다.

---

## 2. 메모리 사용량

| 문장 길이 | Dot Product | Additive |
|-----------|------------|----------|
|64|0.02MB|1MB|
|128|0.06MB|4MB|
|256|0.25MB|16MB|
|512|1MB|64MB|

Additive Attention은 모든 토큰 쌍마다 길이 d의 중간 벡터를 생성하기 때문에
Dot Product보다 약 64배 많은 메모리를 사용하였다.

---

## 3. 학습 파라미터

Dot Product

```
0개
```

Additive

```
8256개
```

Dot Product는 추가 파라미터 없이 행렬곱만 수행하지만,
Additive는 Wq, Wk, v를 학습해야 한다.

---

## 배운 점

성능 자체보다 계산 효율성에서 큰 차이가 있었다.

Transformer는

- 더 빠른 계산
- 더 적은 메모리
- GPU에 최적화된 행렬곱

이라는 장점 때문에 Dot Product Attention을 채택하였다.

---

# 전체 정리

이번 미션을 통해 다음 내용을 직접 확인하였다.

- Self-Attention을 직접 구현하고 PyTorch와 동일한 결과를 얻었다.
- QKᵀ의 분산은 dₖ에 비례함을 실험으로 확인하였다.
- √dₖ로 나누는 이유가 Softmax의 포화를 막기 위한 것임을 이해하였다.
- Dot Product Attention은 Additive Attention보다 훨씬 빠르고 메모리 사용량도 적다는 것을 실험으로 확인하였다.

결과적으로 Transformer 논문의 핵심 설계가 실제 실험 결과와 일치함을 확인할 수 있었다.
