import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")

    corpus = crawl(sys.argv[1])

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    ranks = iterate_pagerank(corpus, DAMPING)
    print("PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a set of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue

        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(
                r'<a\s+(?:[^>]*?)href="([^"]*)"',
                contents
            )
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    """
    num_pages = len(corpus)
    distribution = {}

    links = corpus[page]

    # If page has no outgoing links
    if len(links) == 0:
        for p in corpus:
            distribution[p] = 1 / num_pages
        return distribution

    # Base probability for every page
    for p in corpus:
        distribution[p] = (1 - damping_factor) / num_pages

    # Add probability for linked pages
    for link in links:
        distribution[link] += damping_factor / len(links)

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling n pages
    according to transition model.
    """
    counts = {
        page: 0 for page in corpus
    }

    # First random page
    current_page = random.choice(list(corpus.keys()))
    counts[current_page] += 1

    # Remaining samples
    for _ in range(1, n):
        model = transition_model(
            corpus,
            current_page,
            damping_factor
        )

        current_page = random.choices(
            list(model.keys()),
            weights=list(model.values()),
            k=1
        )[0]

        counts[current_page] += 1

    pagerank = {}

    for page in counts:
        pagerank[page] = counts[page] / n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    """
    num_pages = len(corpus)

    ranks = {
        page: 1 / num_pages
        for page in corpus
    }

    while True:

        new_ranks = {}

        for page in corpus:

            total = 0

            for other_page in corpus:

                links = corpus[other_page]

                # Pages with no links count as linking to every page
                if len(links) == 0:
                    total += ranks[other_page] / num_pages

                elif page in links:
                    total += ranks[other_page] / len(links)

            new_ranks[page] = (
                (1 - damping_factor) / num_pages
                + damping_factor * total
            )

        converged = True

        for page in corpus:
            if abs(new_ranks[page] - ranks[page]) > 0.001:
                converged = False
                break

        ranks = new_ranks

        if converged:
            break

    return ranks


if __name__ == "__main__":
    main()