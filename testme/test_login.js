const { chromium } = require("playwright");

(async () => {
  console.log("🚀 브라우저 시작...");
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 콘솔 로그 캡처
  page.on("console", (msg) => {
    console.log(`[Browser Console] ${msg.type()}: ${msg.text()}`);
  });

  try {
    console.log("📍 로그인 페이지로 이동 중...");
    await page.goto("http://localhost:3000/login", {
      waitUntil: "networkidle",
      timeout: 10000,
    });

    await page.waitForTimeout(2000);
    const currentUrl = page.url();
    console.log(`✅ 현재 URL: ${currentUrl}`);

    // 개발자 로그인 버튼 찾기
    console.log("\n🔍 개발자 로그인 버튼 찾는 중...");
    const devLoginButton = await page.$("#dev-login-button");
    
    if (devLoginButton) {
      console.log("✅ 개발자 로그인 버튼 발견!");
      
      console.log("\n🖱️  개발자 로그인 버튼 클릭...");
      await devLoginButton.click();
      
      // 대시보드로 이동 대기
      await page.waitForTimeout(3000);
      const dashboardUrl = page.url();
      console.log(`✅ 대시보드 이동 후 URL: ${dashboardUrl}`);
      
      if (dashboardUrl.includes("/dashboard")) {
        console.log("✅ 성공! 대시보드로 이동했습니다.");
        
        // 다시 로그인 페이지로 이동
        console.log("\n🔙 로그인 페이지로 다시 이동...");
        await page.goto("http://localhost:3000/login", {
          waitUntil: "networkidle",
          timeout: 10000,
        });
        
        await page.waitForTimeout(2000);
        console.log(`✅ 현재 URL: ${page.url()}`);
        
        // "이미 로그인되어 있습니다" 텍스트 확인
        const loggedInText = await page.textContent("h2");
        console.log(`✅ 페이지 제목: ${loggedInText}`);
        
        if (loggedInText && loggedInText.includes("이미 로그인되어 있습니다")) {
          console.log("✅ '이미 로그인되어 있습니다' 화면 확인!");
          
          // 로그아웃 버튼 찾기
          console.log("\n🔍 로그아웃 버튼 찾는 중...");
          const logoutButton = await page.getByRole('button', { name: /로그아웃/ });
          
          if (logoutButton) {
            console.log("✅ 로그아웃 버튼 발견!");
            console.log("⏳ 5초 대기 중... (화면을 확인하세요)");
            await page.waitForTimeout(5000);
          } else {
            console.log("❌ 로그아웃 버튼을 찾을 수 없습니다.");
          }
        }
      } else {
        console.log(`❌ 실패! 예상치 못한 URL: ${dashboardUrl}`);
      }
    } else {
      console.log("❌ 개발자 로그인 버튼을 찾을 수 없습니다.");
    }

    // 10초 대기 (브라우저 확인용)
    console.log("\n⏳ 10초 추가 대기 중... (브라우저를 확인하세요)");
    await page.waitForTimeout(10000);
  } catch (error) {
    console.error("❌ 에러 발생:", error.message);
  } finally {
    await browser.close();
    console.log("✅ 테스트 완료!");
  }
})();

