(function () {
  "use strict";

  const container = document.getElementById("tabela");
  const endpoint = container.dataset.endpoint;
  const avisoBox = document.getElementById("aviso");
  const buscaInput = document.getElementById("busca");
  const statusSelect = document.getElementById("filtro-status");

  // Distingue "agenda vazia" de "busca sem resultado" no placeholder da tabela.
  let filtroAtivo = false;

  function slug(valor) {
    return (valor || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function statusBadge(cell) {
    const valor = cell.getValue() || "";
    return '<span class="badge badge-' + (slug(valor) || "neutro") + '">' + valor + "</span>";
  }

  const tabela = new Tabulator(container, {
    ajaxURL: endpoint,
    ajaxResponse: function (url, params, response) {
      mostrarAviso(response && response.aviso);
      const dados = (response && response.agendamentos) || [];
      popularStatus(dados);
      return dados;
    },
    layout: "fitColumns",
    responsiveLayout: "collapse",
    placeholder: function () {
      return filtroAtivo
        ? "Nenhum resultado para sua busca."
        : "Nenhum agendamento encontrado.";
    },
    pagination: true,
    paginationMode: "local",
    paginationSize: 8,
    paginationSizeSelector: [8, 15, 30],
    paginationCounter: "rows",
    movableColumns: true,
    initialSort: [
      { column: "data", dir: "asc" },
      { column: "horario", dir: "asc" },
    ],
    columns: [
      { title: "Data", field: "data", sorter: "string", minWidth: 110, responsive: 0 },
      { title: "Hora", field: "horario", sorter: "string", minWidth: 90, responsive: 3 },
      { title: "Paciente", field: "paciente", sorter: "string", minWidth: 160, widthGrow: 2, responsive: 0 },
      { title: "CPF", field: "cpf", sorter: "string", minWidth: 150, responsive: 1 },
      { title: "Especialidade", field: "especialidade", sorter: "string", minWidth: 140, responsive: 4 },
      { title: "Médico", field: "medico", sorter: "string", minWidth: 160, widthGrow: 2, responsive: 2 },
      { title: "Convênio", field: "convenio", sorter: "string", minWidth: 130, responsive: 5 },
      { title: "Status", field: "status", formatter: statusBadge, hozAlign: "center", minWidth: 120, responsive: 1 },
    ],
  });

  function aplicarFiltros() {
    const termo = (buscaInput.value || "").trim().toLowerCase();
    const status = statusSelect.value;
    filtroAtivo = Boolean(termo || status);
    tabela.setFilter(function (linha) {
      const casaTermo =
        !termo ||
        (linha.paciente || "").toLowerCase().includes(termo) ||
        (linha.cpf || "").toLowerCase().includes(termo) ||
        (linha.medico || "").toLowerCase().includes(termo);
      const casaStatus = !status || linha.status === status;
      return casaTermo && casaStatus;
    });
  }

  function popularStatus(dados) {
    const selecionado = statusSelect.value;
    const valores = [...new Set(dados.map((d) => d.status).filter(Boolean))].sort();
    statusSelect.length = 1;
    valores.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      statusSelect.appendChild(opt);
    });
    if (valores.includes(selecionado)) statusSelect.value = selecionado;
  }

  function mostrarAviso(aviso) {
    if (aviso) {
      avisoBox.textContent = aviso;
      avisoBox.hidden = false;
    } else {
      avisoBox.hidden = true;
      avisoBox.textContent = "";
    }
  }

  buscaInput.addEventListener("input", aplicarFiltros);
  statusSelect.addEventListener("change", aplicarFiltros);
})();
