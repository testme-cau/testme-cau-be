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
    console.log("📍 대시보드로 이동 중...");
    await page.goto("http://localhost:3000/dashboard", {
      waitUntil: "networkidle",
      timeout: 10000,
    });

    // 현재 URL 확인
    const currentUrl = page.url();
    console.log(`✅ 현재 URL: ${currentUrl}`);

    if (currentUrl.includes("/dashboard")) {
      console.log("✅ 성공! 대시보드에 머물러 있습니다.");
    } else if (currentUrl.includes("/login")) {
      console.log("❌ 실패! /login으로 리다이렉트되었습니다.");
    } else {
      console.log(`⚠️  예상치 못한 URL: ${currentUrl}`);
    }

    // 페이지 제목 확인
    const title = await page.title();
    console.log(`📄 페이지 제목: ${title}`);

    // 새로고침 테스트
    console.log("\n🔄 새로고침 테스트...");
    await page.reload({ waitUntil: "networkidle" });
    const urlAfterReload = page.url();
    console.log(`✅ 새로고침 후 URL: ${urlAfterReload}`);

    if (urlAfterReload.includes("/dashboard")) {
      console.log("✅ 새로고침 후에도 대시보드에 머물러 있습니다!");
    } else {
      console.log("❌ 새로고침 후 다른 페이지로 이동했습니다.");
    }

    // 5초 대기 (브라우저 확인용)
    console.log("\n⏳ 5초 대기 중... (브라우저를 확인하세요)");
    await page.waitForTimeout(5000);
  } catch (error) {
    console.error("❌ 에러 발생:", error.message);
  } finally {
    await browser.close();
    console.log("✅ 테스트 완료!");
  }
})();

