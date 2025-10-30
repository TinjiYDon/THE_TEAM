const apiBase = "/api/v1";

async function uploadInvoice(e) {
  e.preventDefault();
  const fileInput = document.getElementById("invoiceFile");
  const userId = document.getElementById("userIdUpload").value || 1;
  const out = document.getElementById("uploadResult");
  if (!fileInput.files.length) {
    out.textContent = "请选择文件";
    return;
  }
  const form = new FormData();
  form.append("file", fileInput.files[0]);
  try {
    const res = await fetch(`${apiBase}/invoices/upload?user_id=${userId}`, {
      method: "POST",
      body: form,
    });
    const data = await res.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = `错误: ${err}`;
  }
}

async function loadBills() {
  const userId = document.getElementById("userIdBills").value || 1;
  const tbody = document.querySelector("#billsTable tbody");
  tbody.innerHTML = "<tr><td colspan=5>加载中...</td></tr>";
  try {
    const res = await fetch(`${apiBase}/bills?user_id=${userId}&limit=20`);
    const data = await res.json();
    const bills = data.data || [];
    tbody.innerHTML = bills
      .map(
        (b) => `
      <tr>
        <td>${b.consume_time?.replace("T"," ") || ""}</td>
        <td>${b.merchant || ""}</td>
        <td>${b.category || ""}</td>
        <td class="num">${Number(b.amount || 0).toFixed(2)}</td>
        <td>${b.payment_method || ""}</td>
      </tr>`
      )
      .join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan=5>错误: ${err}</td></tr>`;
  }
}

async function loadSummary() {
  const userId = document.getElementById("userIdSummary").value || 1;
  const container = document.getElementById("summary");
  container.textContent = "加载中...";
  try {
    const res = await fetch(`${apiBase}/analysis/summary?user_id=${userId}`);
    const data = await res.json();
    const s = data.data || {};
    const cats = s.categories || s.spending_by_category || {};
    container.innerHTML = `
      <div class="grid">
        <div class="stat"><div class="label">总金额</div><div class="value">${Number(s.total_amount||0).toFixed(2)} 元</div></div>
        <div class="stat"><div class="label">总笔数</div><div class="value">${s.total_count ?? 0} 笔</div></div>
        <div class="stat"><div class="label">平均金额</div><div class="value">${Number(s.avg_amount||s.average_spending_per_bill||0).toFixed(2)} 元</div></div>
      </div>
      <h3>按类别</h3>
      <ul class="cats">
        ${Object.keys(cats)
          .map((k) => `<li><span>${k}</span><b>${Number(cats[k]?.total_amount ?? cats[k] ?? 0).toFixed(2)}</b></li>`)
          .join("")}
      </ul>
    `;
  } catch (err) {
    container.textContent = `错误: ${err}`;
  }
}

document.getElementById("uploadForm").addEventListener("submit", uploadInvoice);
document.getElementById("refreshBills").addEventListener("click", loadBills);
document.getElementById("refreshSummary").addEventListener("click", loadSummary);

// 初始加载
loadBills();
loadSummary();


