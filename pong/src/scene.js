import * as THREE from 'three';
import { font } from './main';

export function createScene() {
  const scene = new THREE.Scene();
  return scene;
}

export function createCamera() {
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 15, 10);
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
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);
  const pointLight = new THREE.PointLight(0xffffff, 0.5);
  pointLight.position.set(0, 50, 50);
  scene.add(pointLight);
}

export function createTable(scene) {
  const tableGeometry = new THREE.PlaneGeometry(10, 20);
  const tableMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
  const table = new THREE.Mesh(tableGeometry, tableMaterial);
  table.rotation.x = -Math.PI / 2;  // Make it horizontal
  scene.add(table);
}

export function updateTextMesh(mesh, text) {
	if (!mesh){
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
	  mesh.geometry.dispose();
	  mesh.geometry = geometry;
	});
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

export { font };
