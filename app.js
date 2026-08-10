document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize AOS Animation
    AOS.init({
        once: true,
        duration: 800,
        easing: 'ease-out-cubic'
    });

    // 2. Hide Loading Screen
    const loadingScreen = document.getElementById("loading-screen");
    setTimeout(() => {
        if (loadingScreen) {
            loadingScreen.style.opacity = "0";
            setTimeout(() => loadingScreen.remove(), 700);
        }
    }, 400);

    // 3. Scroll Progress Bar
    const progressBar = document.getElementById("scroll-progress");
    window.addEventListener("scroll", () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        if (progressBar) progressBar.style.width = scrolled + "%";
    });

    // 4. Mouse Parallax Effect on Hero Dashboard
    const heroCard = document.getElementById("hero-card");
    if (heroCard && window.innerWidth > 1024) {
        document.addEventListener("mousemove", (e) => {
            const { clientX, clientY } = e;
            const x = (clientX / window.innerWidth - 0.5) * 15;
            const y = (clientY / window.innerHeight - 0.5) * 15;
            heroCard.style.transform = `perspective(1000px) rotateY(${x}deg) rotateX(${-y}deg)`;
        });
    }

    // 5. Animated Number Counters
    const counters = document.querySelectorAll(".counter");
    const observerOptions = { threshold: 0.5 };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const updateCount = () => {
                    const dest = +target.getAttribute("data-target");
                    const count = +target.innerText;
                    const speed = dest / 40;
                    if (count < dest) {
                        target.innerText = Math.ceil(count + speed);
                        setTimeout(updateCount, 30);
                    } else {
                        target.innerText = dest.toLocaleString() + "+";
                    }
                };
                updateCount();
                obs.unobserve(target);
            }
        });
    }, observerOptions);

    counters.forEach(counter => observer.observe(counter));
});
