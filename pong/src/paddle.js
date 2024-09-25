import * as THREE from 'three';

export function createPaddle(color, x, z) {
  const paddleGeometry = new THREE.BoxGeometry(2, 0.5, 0.5);
  const paddleMaterial = new THREE.MeshPhongMaterial({ color });
  const paddle = new THREE.Mesh(paddleGeometry, paddleMaterial);
  paddle.position.set(x, 0.25, z);
  return paddle;
}
