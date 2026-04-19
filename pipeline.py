from agents import reader_agent, search_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str) -> str:

    state = {}

    # search agent
    print("\n" + "=" * 50)
    print("Step-1 -- search agent is working")
    print("=" * 50)

    Search_agent = search_agent()
    Search_result = Search_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Find recent, reliable and detailed information about: {topic}",
                )
            ]
        }
    )
    raw_search = Search_result["messages"][-1].content
    state["search_results"] = (
        raw_search[0]["text"] if isinstance(raw_search, list) else raw_search
    )
    print("\n search result", state["search_results"])

    # reader agent
    print("\n" + "=" * 50)
    print("Step-2 -- reader agent is working")
    print("=" * 50)

    reader_inst = reader_agent()
    Reader_result = reader_inst.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}",
                )
            ]
        }
    )
    raw_read = Reader_result["messages"][-1].content
    state["scraped_content"] = raw_read[0]["text"] if isinstance(raw_read, list) else raw_read
    print("\n[Scraped Content]\n", state["scraped_content"])

    # writer chain
    print("\n" + "=" * 50)
    print("Step-3 -- writer is drafting the report")
    print("=" * 50)

    research_combined = (
        f"search results : \n {state['search_results']}\n\n"
        f"detailed scraped content : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke(
        {"topic": topic, "research": research_combined}
    )

    print("\n Final report \n", state["report"])

    # critic report
    print("\n" + "=" * 50)
    print("Step-4 -- critic is reviewing the report")
    print("=" * 50)

    critic_result = critic_chain.invoke({"report": state["report"]})
    state["feedback"] = critic_result[0]["text"] if isinstance(critic_result, list) else critic_result
    print("\n[Critic Report]\n", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\n Enter your research topic : ")
    run_research_pipeline(topic)
