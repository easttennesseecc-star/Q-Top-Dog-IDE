import time, asyncio
from backend.services.semantic_analysis import get_analyzer

code = '\n'.join([f'variable_{i} = {i}' for i in range(100)])

async def run():
    analyzer = get_analyzer()
    t0 = time.perf_counter()
    result = await analyzer.analyze_code(code, 'python')
    analysis_ms = (time.perf_counter() - t0) * 1000
    t1 = time.perf_counter()
    completions = analyzer.get_completions(result['symbols'], 'var')
    completions_ms = (time.perf_counter() - t1) * 1000
    print('ANALYSIS_MS', f'{analysis_ms:.2f}', 'COMPLETIONS_MS', f'{completions_ms:.2f}', 'TOTAL_MS', f'{(analysis_ms+completions_ms):.2f}', 'COUNT', len(completions))

if __name__ == '__main__':
    asyncio.run(run())
