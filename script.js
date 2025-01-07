function animarFondo() {
  let angle = 0;
  const fondo = document.getElementById('fondoAnimado');

  setInterval(() => {
      angle = (angle + 1) % 360;
      const color1 = `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
      const color2 = `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
      
      fondo.style.opacity = 0;

      setTimeout(() => {
          fondo.style.backgroundImage = `linear-gradient(${angle}deg, ${color1}, ${color2})`;
          fondo.style.opacity = 0;
          requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                  fondo.style.opacity = 1;
              });
          });
      }, 2000); 
  }, 5000); 
}

document.addEventListener('DOMContentLoaded', animarFondo);

