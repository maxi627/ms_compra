import { check, sleep } from 'k6';
import http from 'k6/http';

// Configuración del test
export let options = {
  stages: [
    { duration: '10s', target: 10 }, // Subir a 10 usuarios en 10s
    { duration: '30s', target: 50 }, // Mantener 50 usuarios por 30s
    { duration: '10s', target: 0 },  // Bajar a 0 usuarios en 10s
  ],
};

export default function () {
  let res = http.get('http://compra.localhost/api/v1/compra');

  check(res, {
    'status es 200': (r) => r.status === 200,
    'respuesta en menos de 200ms': (r) => r.timings.duration < 200,
  });

  sleep(1); // Esperar 1 segundo entre solicitudes
}
