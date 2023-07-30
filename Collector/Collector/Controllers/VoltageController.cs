using Microsoft.AspNetCore.Mvc;

namespace Collector.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class VoltageController : ControllerBase
    {
        private readonly ILogger<VoltageController> _logger;
        public VoltageController(ILogger<VoltageController> logger)
        {
            _logger = logger;
        }

        [HttpPost]
        public IActionResult Post([FromBody] float voltage)
        {
            _logger.LogInformation("{voltage}", voltage);
            return Ok();
        }
    }
}
