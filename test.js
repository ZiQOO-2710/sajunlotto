// 필요한 부품을 가져오는 것은 동일합니다.
const { chromium } = require('playwright');

async function main() {
  console.log("플레이라이트 로봇을 작동시킵니다...");

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto('https://www.naver.com');
  console.log("네이버에 접속했습니다.");

  await page.fill('#query', '오늘 날씨');
  console.log("'오늘 날씨'를 입력했습니다.");

  await page.press('#query', 'Enter');
  console.log("엔터 키를 눌러 검색을 실행했습니다.");

  // ⭐⭐⭐ 새로운 임무 추가! ⭐⭐⭐
  // 1. 날씨 정보가 화면에 나타날 때까지 잠시 기다려줍니다.
  //    우리가 찾은 주소('.temperature_text')를 사용합니다.
  await page.waitForSelector('.temperature_text');
  console.log("날씨 정보를 찾았습니다!");

  // 2. 해당 주소('.temperature_text')에 있는 요소를 찾아서
  //    그 안에 있는 텍스트(innerText)를 가져옵니다.
  const temperature = await page.locator('.temperature_text').innerText();

  // 3. 가져온 결과를 터미널에 출력합니다!
  console.log('가져온 현재 온도는:', temperature);
  // ⭐⭐⭐ 임무 추가 완료! ⭐⭐⭐

  // 확인을 위해 잠시 2초만 더 기다렸다가 브라우저를 닫습니다.
  await page.waitForTimeout(2000);

  await browser.close();
  console.log("임무 완료! 브라우저를 닫습니다.");
}

main();