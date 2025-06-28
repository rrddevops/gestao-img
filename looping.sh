#!/bin/bash

# Lista de CPFs
cpfs=(
  "88888888888"
  "77777777777"
  "66666666666"
  "55555555555"
  "44444444444"
  "33333333333"
  "22222222222"
  "11111111111"
  "00000000000"
)

# Loop infinito
while true; do
  for cpf in "${cpfs[@]}"; do
    echo "Enviando CPF: $cpf"
    curl --silent --location 'http://localhost:5002/schedule' \
      --header 'Content-Type: application/json' \
      --data "{\"cpf\": \"$cpf\"}"
    echo -e "\nAguardando 30 segundos..."
    sleep 5
  done
done
