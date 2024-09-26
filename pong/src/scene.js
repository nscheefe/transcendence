import * as THREE from 'three';
import { font } from './main';
import { damp } from 'three/src/math/MathUtils.js';

export function createScene() {
  const scene = new THREE.Scene();
  return scene;
}

export function createCamera() {
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 20, 0);
  camera.lookAt(0, 0, 0);
  return camera;
}

export function createRenderer() {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);
  return renderer;
}

export function createLights(scene) {
	const ambientLight = new THREE.AmbientLight("#ffffff", 200);
	  scene.add(ambientLight);

	  const spotlight = new THREE.SpotLight("#d53c3d", 20, 500, Math.PI * 0.1, 5);
	spotlight.position.set(10, 15, 2.2);
	spotlight.target.position.set(-5, 5, 5);
	  scene.add(spotlight);
	  scene.add(spotlight.target);

	  const spotlight2 = new THREE.SpotLight("#d53c3d", 20, 500, Math.PI * 0.1, 5);
	  spotlight2.position.set(-10, 15, 2.2);
	  spotlight2.target.position.set(5, 5, 5);
	  scene.add(spotlight2);
	  scene.add(spotlight2.target);
}

export function createTable() {
  const tableGeometry = new THREE.PlaneGeometry(10, 20, 1, 2);
  const tableMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00, transparent: true, opacity: 0 });
  const table = new THREE.Mesh(tableGeometry, tableMaterial);
  table.rotation.x = -Math.PI / 2;  // Make it horizontal
  return table;
  scene.add(table);
}

export function createTextOnTable(font, scene, text, offsetY, table) {
  const geometry = new THREE.TextGeometry(text, {
    font: font,
    size: 1,
    height: 0.1,
  });
  const material = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const mesh = new THREE.Mesh(geometry, material);

  geometry.computeBoundingBox();
  const boundingBox = geometry.boundingBox;
  const textWidth = boundingBox.max.x - boundingBox.min.x;

  mesh.position.set(-(textWidth / 2) , offsetY, 0);

  // Add the text mesh as a child of the table mesh
  table.add(mesh);
  return mesh;
}

export function updateTextMeshOrientation(textMesh, camera) {
  if (textMesh) {
	const cameraDirection = new THREE.Vector3();
	camera.getWorldDirection(cameraDirection);
	textMesh.rotation.z = camera.rotation.z;
  }
}

  export function updateTextMesh(mesh, text, camera) {
	if (!mesh) {
	  console.log("text mesh is null");
	  return;
	}
	const loader = new THREE.FontLoader();
	loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', (font) => {
	  const geometry = new THREE.TextGeometry(text, {
		font: font,
		size: 1,
		height: 0.1,
	  });
	  geometry.computeBoundingBox();
	  const boundingBox = geometry.boundingBox;
	  const textWidth = boundingBox.max.x - boundingBox.min.x;
	  mesh.geometry.dispose();
	  mesh.geometry = geometry;
	//  mesh.position.x = -textWidth / 2;  // Center the text horizontally
	  updateTextMeshOrientation(mesh, camera);
	});
  }

export function createTextMeshRelativeToCamera(text, size, color, camera, offset = { x: 0, y: 0, z: -5 }) {
	const geometry = new THREE.TextGeometry(text, {
	  font: font,
	  size: size,
	  height: 0.1,
	});
	const material = new THREE.MeshBasicMaterial({ color: color });
	const mesh = new THREE.Mesh(geometry, material);
	updateTextPositionRelativeToCamera(mesh, camera, offset);
	return mesh;
}

export function createTextMesh(text, size, color, position) {
	const geometry = new THREE.TextGeometry(text, {
	  font: font,
	  size: size,
	  height: 0.1,
	});
	const material = new THREE.MeshBasicMaterial({ color: color });
	const mesh = new THREE.Mesh(geometry, material);
	mesh.position.set(position.x, position.y, position.z);
	return mesh;
}

export function gameOver(winner) {
  const gameOverText = createTextMesh('Game Over', 2, 0xff0000, { x: -2, y: 1, z: 0 });
  return gameOverText;
}

export function updateTextPositionRelativeToCamera(textMesh, camera, offset = { x: 0, y: 0, z: -5 }) {
	const cameraDirection = new THREE.Vector3();
	camera.getWorldDirection(cameraDirection);
	textMesh.position.copy(camera.position).add(cameraDirection.multiplyScalar(offset.z));
	textMesh.position.x += offset.x;
	textMesh.position.y += offset.y;
  }

export { font };
